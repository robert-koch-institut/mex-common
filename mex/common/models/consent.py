# XXX this is a forward-compatibility hint for feature/model-update-v3

# when this gets merged with model v3
# - remove the `Annotated[..., Field(examples=["https://mex..."])]` from all enum fields
# - add `Annotated[..., AfterValidator(Identifier)]` to all identifier union fields
