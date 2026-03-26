import strawberry
from strawberry.extensions import MaskErrors

from .mutations import Mutation
from .queries import Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[MaskErrors(should_mask_error=lambda _err, _info: True)],
)
