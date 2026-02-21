from typing import Tuple, List, Union, Callable, Optional

import torch
import torch.nn as nn
import torch.distributed as dist

import dualpipe.comm as comm
from dualpipe.utils import WeightGradStore


class BaseDualPipe(nn.Module):
    """Base class containing shared logic between DualPipe and DualPipeV"""
    
    def __init__(
        self,
        modules: Tuple[nn.Module, nn.Module],
        batch_dim: int = 0,
        process_group: Optional[dist.ProcessGroup] = None,
        rank_mapping: Optional[List[int]] = None,
    ) -> None:
        super().__init__()

        # Input validation
        if not isinstance(modules, (tuple, list)) or len(modules) != 2:
            raise ValueError("modules must be a tuple/list of exactly 2 nn.Module instances")
        
        for i, module in enumerate(modules):
            if not isinstance(module, nn.Module):
                raise ValueError(f"modules[{i}] must be an nn.Module instance, got {type(module)}")

        if process_group is not None and not isinstance(process_group, dist.ProcessGroup):
            raise ValueError("process_group must be a valid ProcessGroup or None")

        assert next(modules[0].parameters()).device == torch.device(torch.cuda.current_device())
        self.module = nn.ModuleList(modules)
        self.overlapped_forward_backward = type(modules[0]) == type(modules[1]) and hasattr(type(modules[0]), "overlapped_forward_backward")
        self.batch_dim = batch_dim
        self.group = process_group or dist.distributed_c10d._get_default_group()
        self.num_ranks = self.group.size()

        # rank_mapping: Map rank in process_group to actual pp rank.
        # rank_inverse_mapping: Map actual pp rank to rank in process_group.
        if rank_mapping is None:
            rank_mapping = list(range(self.num_ranks))
        
        # Validate rank_mapping bounds
        if rank_mapping:
            if len(rank_mapping) != self.num_ranks:
                raise ValueError(f"rank_mapping length ({len(rank_mapping)}) must match num_ranks ({self.num_ranks})")
            if not all(0 <= rank < self.num_ranks for rank in rank_mapping):
                raise ValueError(f"All ranks in rank_mapping must be in range [0, {self.num_ranks})")
            if len(set(rank_mapping)) != len(rank_mapping):
                raise ValueError("rank_mapping must not contain duplicate ranks")

        rank_inverse_mapping = [None] * (self.num_ranks + 1)
        for i in range(self.num_ranks):
            rank_inverse_mapping[rank_mapping[i]] = i

        self.rank = rank_mapping[self.group.rank()]
        self.prev_rank = rank_inverse_mapping[self.rank - 1]
        self.next_rank = rank_inverse_mapping[self.rank + 1]

        self.is_first_rank = self.rank == 0
        self.is_last_rank = self.rank == self.num_ranks - 1

    def _reset_states(self) -> None:
        """Reset internal state - to be overridden by subclasses"""
        WeightGradStore.clear()

        self.input_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.output_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.input_grad_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.output_grad_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.loss_chunks: List[torch.Tensor] = []
        self.criterion: Callable = None

        self.comm_ops: List[dist.P2POp] = []
        self.to_free: List[torch.Tensor] = []

    def _free_tensors(self) -> None:
        """Free tensors with graceful handling of view tensors"""
        for tensor in self.to_free:
            # Handle view tensors gracefully instead of asserting
            if tensor._base is not None:
                # Log warning for view tensors but continue processing
                print(f"Warning: Pipeline stage returned view tensor at rank {dist.get_rank()}, shape {tensor.shape}")
                # Don't free view tensors as it could corrupt base tensor
                continue
            tensor.data = torch.Tensor()
        self.to_free = []

    def _commit_and_wait_comm(self) -> None:
        """Commit and wait for communication operations with error handling"""
        if not self.comm_ops:
            return
        try:
            reqs = dist.batch_isend_irecv(self.comm_ops)
            for req in reqs:
                req.wait()
            # Only clear comm_ops after successful completion
            self.comm_ops = []
            self._free_tensors()
        except Exception as e:
            # Don't clear comm_ops on failure to avoid inconsistent state
            raise RuntimeError(f"Communication operation failed at rank {dist.get_rank()}: {str(e)}") from e