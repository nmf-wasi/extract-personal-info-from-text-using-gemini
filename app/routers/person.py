from fastapi import APIRouter, Depends, HTTPException, status
from app.llm import extract_personal_info, LLMBadOutput, LLMUnavailable
from app.schemas.person import PersonalInfo
from app.schemas.extract import ExtractRequest

router = APIRouter()


def get_extractor():
    return extract_personal_info


@router.post("/extract", response_model=PersonalInfo)
def extract(request: ExtractRequest, extractor=Depends(get_extractor)):
    try:
        response = extractor(request.text)

    except LLMBadOutput:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model returned unusable output!",
        )
    except LLMUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM temporarily unavailable, retry later!",
        )
    if not response.is_personal_info:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Text is not about personal information!",
        )
    print(response)
    return response
