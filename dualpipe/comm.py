from typing import List, Tuple

import torch
import torch.distributed as dist


TENSOR_SHAPES: List[Tuple[int]] = None
TENSOR_DTYPE: torch.dtype = None


def set_p2p_tensor_shapes(shapes: List[Tuple[int]]):
    global TENSOR_SHAPES
    TENSOR_SHAPES = shapes


def set_p2p_tensor_dtype(dtype: torch.dtype):
    global TENSOR_DTYPE
    TENSOR_DTYPE = dtype


def build_from_tensor_shapes():
    if TENSOR_SHAPES is None or TENSOR_DTYPE is None:
        raise ValueError("TENSOR_SHAPES and TENSOR_DTYPE must be set before building tensors")
    
    tensors = []
    for s in TENSOR_SHAPES:
        if s is not None and len(s) > 0:  # Check for valid shapes
            tensors.append(torch.empty(s, dtype=TENSOR_DTYPE, device="cuda", requires_grad=True))
        else:
            tensors.append(None)
    return tensors


def append_irecv(ops: List[dist.P2POp], src: int, group: dist.ProcessGroup) -> List[torch.Tensor]:
    tensors = build_from_tensor_shapes()
    src = dist.distributed_c10d.get_global_rank(group, src)
    for tensor in tensors:
        if tensor is not None:
            ops.append(dist.P2POp(dist.irecv, tensor, src))
    return tensors


def append_isend(ops: List[dist.P2POp], tensors: List[torch.Tensor], dst: int, group: dist.ProcessGroup) -> None:
    if tensors is None:
        return  # Early return for None tensors list
    
    dst = dist.distributed_c10d.get_global_rank(group, dst)
    for tensor in tensors:
        if tensor is not None:
            ops.append(dist.P2POp(dist.isend, tensor, dst))
