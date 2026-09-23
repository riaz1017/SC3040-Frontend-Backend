from app.config import settings
from app.models import AcademicQuery


class QueryAnalysisService:
    def analyse(self, query: AcademicQuery) -> None:
        if settings.matching_fallback:
            query.fallback_mode = True
            query.analysis_topic = None
            query.analysis_concepts = None
            query.analysis_difficulty = None
            query.analysis_confidence = None
            return

        words = [w.strip(".,!?") for w in query.text.split() if len(w.strip(".,!?")) > 3]
        query.fallback_mode = False
        query.analysis_topic = " ".join(words[:8]) or query.module
        query.analysis_concepts = words[:5]
        query.analysis_difficulty = "medium"
        query.analysis_confidence = 0.72
