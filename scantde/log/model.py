from pydantic import Field,  BaseModel

class ProcStage(BaseModel):
    """
    A pydantic model for a processing stage
    """
    stage: str = Field(min_length=1, description="Name of the processing stage")
    n_sources: int = Field(ge=0, description="Number of candidates processed in this stage")
    tdes: list[str] = Field(description="List of TDE names")