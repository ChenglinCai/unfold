"""Field types that every file format shares.

They live outside `unfold.formats`, so a module such as `unfold.visuals.params`
can use them without loading every format first. That load would close a cycle,
because the episode formats import the visual parameters.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]*$")]
# A pointer to one place in a source: the source id, then #, then the anchor id.
Ref = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]*#[a-z0-9][a-z0-9-]*$")
]
Text = Annotated[str, StringConstraints(min_length=1)]


class Model(BaseModel):
    """A part of a file format. Unknown fields fail, so typos show up."""

    model_config = ConfigDict(extra="forbid")
