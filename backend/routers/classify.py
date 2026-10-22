from fastapi import APIRouter, Depends
from classifier import get_classifier, ComplaintClassifier
from schemas import ClassifyRequest, ClassifyResponse

router = APIRouter(prefix="/api/classify", tags=["classify"])

@router.post("", response_model=ClassifyResponse)
def classify_text_or_image(
    request: ClassifyRequest,
    classifier: ComplaintClassifier = Depends(get_classifier)
):
    """
    Multimodal classification of a civic complaint into Department and Priority Score.
    Evaluates Text description, Picture evidence, and Location (manual address or GPS).
    """
    result = classifier.classify_complaint(
        text=request.text or "",
        image_data=request.image_data,
        location_address=request.location_address,
        location_lat=request.location_lat,
        location_lng=request.location_lng
    )
    return ClassifyResponse(**result)
