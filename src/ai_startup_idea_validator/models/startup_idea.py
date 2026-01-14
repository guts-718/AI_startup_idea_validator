from typing import List, Optional
from pydantic import BaseModel, Field

class StartupIdea(BaseModel):
    # required
    problem: str = Field(..., description="Core problem being solved")
    solution: str = Field(..., description="Solution proposed")
    geography: str= Field(..., description="target geography/ location/ market")

    # optional but recommended (penalty wala)
    target_user: Optional[str]=Field(None, description="target audience")
    industry: Optional[str]=Field(None, description="industry , sector or domain")
    differentiation: Optional[str]=Field(None, description="why is this solution different from others")
    monetization_model: Optional[str]=Field(None, description="how will the startup make money")
    founder_expertise: Optional[str]=Field(None, description="Founder's relevant background for the startup")

    # kindof optionl
    customer_acquisition: Optional[str]=Field(None, description="how users will be acquired")
    regulatory_constraints: Optional[List[str]]=Field(default_factory=list)
    constraints: Optional[List[str]]=Field(default_factory=list)


    # internal field
    inferred_fields: Optional[List[str]]=Field(default_factory=list)