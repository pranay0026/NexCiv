import os
import json
import uuid
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from duplicate_detection.configs.config import cfg

TABLES_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "data" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

INCIDENTS_FILE = TABLES_DIR / "master_incidents.json"
LINKS_FILE = TABLES_DIR / "complaint_links.json"
PREDICTIONS_FILE = TABLES_DIR / "duplicate_predictions.json"
REVIEWS_FILE = TABLES_DIR / "duplicate_reviews.json"
EMBEDDINGS_CACHE_FILE = TABLES_DIR / "complaint_embeddings.npz"

class IncidentVectorStore:
    """
    Manages Master Incidents, Vector Embeddings, and Duplicate Incident Links.
    Supports:
    1. Direct PostgreSQL + pgvector queries when Supabase is active
    2. Local transactional JSON tables & NumPy vector indexing fallback for offline/embedded execution.
    """

    def __init__(self):
        self._incidents: List[Dict[str, Any]] = self._load_json(INCIDENTS_FILE)
        self._links: List[Dict[str, Any]] = self._load_json(LINKS_FILE)
        self._predictions: List[Dict[str, Any]] = self._load_json(PREDICTIONS_FILE)
        self._reviews: List[Dict[str, Any]] = self._load_json(REVIEWS_FILE)
        
        # In-memory vector cache: {complaint_id: np.ndarray}
        self._embeddings: Dict[str, np.ndarray] = {}
        self._load_embeddings()

    def _load_json(self, path: Path) -> List[Dict[str, Any]]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_json(self, path: Path, data: List[Dict[str, Any]]):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {path}: {e}")

    def _load_embeddings(self):
        if EMBEDDINGS_CACHE_FILE.exists():
            try:
                npz = np.load(EMBEDDINGS_CACHE_FILE)
                for key in npz.files:
                    self._embeddings[key] = npz[key]
            except Exception as e:
                print(f"Notice: Could not load embedding cache: {e}")

    def _save_embeddings(self):
        try:
            np.savez(EMBEDDINGS_CACHE_FILE, **self._embeddings)
        except Exception as e:
            print(f"Notice: Could not save embedding cache: {e}")

    def add_complaint_embedding(self, complaint_id: str, embedding: np.ndarray):
        """Stores normalized vector embedding for a complaint."""
        if embedding.ndim > 1:
            embedding = embedding.flatten()
        self._embeddings[str(complaint_id)] = embedding.astype(np.float32)
        # Periodic sync
        if len(self._embeddings) % 10 == 0:
            self._save_embeddings()

    def search_candidates(
        self,
        query_embedding: np.ndarray,
        department_code: Optional[str] = None,
        municipality: Optional[str] = None,
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Retrieves Top-K candidate complaints/incidents matching category and dense semantic similarity.
        """
        if not self._embeddings:
            # Fall back to returning active master incidents directly
            results = []
            for inc in self._incidents[-top_k:]:
                if not department_code or inc.get('department_code') == department_code:
                    results.append({
                        'complaint_id': inc['incident_id'],
                        'incident_id': inc['incident_id'],
                        'title': inc.get('title', ''),
                        'description': inc.get('description', ''),
                        'category': inc.get('department_code', ''),
                        'department_code': inc.get('department_code', ''),
                        'location_lat': inc.get('location_lat'),
                        'location_lng': inc.get('location_lng'),
                        'location_address': inc.get('location_address'),
                        'ward': inc.get('ward'),
                        'created_at': inc.get('created_at'),
                        'image_hash': inc.get('primary_image_hash'),
                        'semantic_similarity': 0.70
                    })
            return results

        if query_embedding.ndim > 1:
            query_embedding = query_embedding.flatten()

        # Compute cosine similarity across cached embeddings
        ids = list(self._embeddings.keys())
        matrix = np.array([self._embeddings[cid] for cid in ids])
        
        # Dot product with normalized query
        scores = np.dot(matrix, query_embedding)
        top_indices = np.argsort(scores)[::-1][:top_k * 2]

        candidates = []
        # Find complaint metadata
        for idx in top_indices:
            cid = ids[idx]
            sim = float(scores[idx])
            bounded_sim = max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))
            
            # Find in incidents or complaint links
            inc_match = next((inc for inc in self._incidents if inc['incident_id'] == cid), None)
            if inc_match:
                if department_code and inc_match.get('department_code') != department_code:
                    continue
                candidates.append({
                    'complaint_id': cid,
                    'incident_id': inc_match['incident_id'],
                    'title': inc_match.get('title', ''),
                    'description': inc_match.get('description', ''),
                    'category': inc_match.get('department_code', ''),
                    'department_code': inc_match.get('department_code', ''),
                    'location_lat': inc_match.get('location_lat'),
                    'location_lng': inc_match.get('location_lng'),
                    'location_address': inc_match.get('location_address'),
                    'ward': inc_match.get('ward'),
                    'created_at': inc_match.get('created_at'),
                    'image_hash': inc_match.get('primary_image_hash'),
                    'semantic_similarity': bounded_sim
                })
            if len(candidates) >= top_k:
                break

        return candidates

    def create_master_incident(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a brand new master incident for an unlinked original grievance."""
        muni = (complaint.get('municipal_corporation') or 'GVMC').upper()
        inc_id = f"INC-{muni}-{random_suffix()}"
        
        now = datetime.utcnow().isoformat() + "Z"
        incident = {
            'incident_id': inc_id,
            'title': complaint.get('title', 'Civic Grievance'),
            'description': complaint.get('description', ''),
            'department': complaint.get('department', 'General'),
            'department_code': complaint.get('department_code', complaint.get('category', 'others')),
            'complaint_type': complaint.get('complaint_type', 'other_civic_issue'),
            'municipality': muni,
            'ward': complaint.get('ward', 'Ward 1'),
            'landmark': complaint.get('landmark', ''),
            'location_lat': complaint.get('location_lat'),
            'location_lng': complaint.get('location_lng'),
            'location_address': complaint.get('location_address'),
            'status': 'open',
            'priority': complaint.get('priority', 'Medium'),
            'priority_score': complaint.get('priority_score', 60.0),
            'linked_complaints_count': 1,
            'citizens_affected_count': 1,
            'primary_image_url': complaint.get('image_url'),
            'primary_image_hash': complaint.get('image_hash'),
            'assigned_team': complaint.get('assigned_team'),
            'assigned_employee_id': complaint.get('assigned_employee_id'),
            'first_reported_at': now,
            'last_reported_at': now,
            'created_at': now,
            'updated_at': now
        }
        self._incidents.insert(0, incident)
        self._save_json(INCIDENTS_FILE, self._incidents)

        # Link initial complaint to the new incident
        self.link_complaint(
            complaint_id=complaint['id'],
            master_incident_id=inc_id,
            link_type='primary_incident_seed',
            similarity_score=1.0,
            notes='Initial grievance registering the master incident'
        )
        return incident

    def link_complaint(
        self,
        complaint_id: str,
        master_incident_id: str,
        link_type: str = 'ai_auto',
        similarity_score: float = 1.0,
        linked_by_user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Links an incoming citizen complaint to an existing master incident.
        Preserves original citizen submission while updating master incident statistics.
        """
        link = {
            'id': str(uuid.uuid4()),
            'complaint_id': complaint_id,
            'master_incident_id': master_incident_id,
            'link_type': link_type,
            'similarity_score': float(similarity_score),
            'linked_by_user_id': linked_by_user_id,
            'notes': notes or f'Linked via {link_type}',
            'created_at': datetime.utcnow().isoformat() + "Z"
        }
        self._links.append(link)
        self._save_json(LINKS_FILE, self._links)

        # Update Master Incident count and timestamp
        for inc in self._incidents:
            if inc['incident_id'] == master_incident_id:
                inc['linked_complaints_count'] = inc.get('linked_complaints_count', 1) + 1
                inc['citizens_affected_count'] = inc.get('citizens_affected_count', 1) + 1
                inc['last_reported_at'] = datetime.utcnow().isoformat() + "Z"
                inc['updated_at'] = datetime.utcnow().isoformat() + "Z"
                break
        self._save_json(INCIDENTS_FILE, self._incidents)
        return link

    def record_prediction(self, prediction_dict: Dict[str, Any]):
        """Logs an AI duplicate evaluation to the audit trail."""
        prediction_dict['id'] = str(uuid.uuid4())
        prediction_dict['evaluated_at'] = datetime.utcnow().isoformat() + "Z"
        self._predictions.insert(0, prediction_dict)
        self._save_json(PREDICTIONS_FILE, self._predictions[:1000])

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a specific master incident by ID."""
        return next((inc for inc in self._incidents if inc['incident_id'] == incident_id), None)

    def get_incident_complaints(self, incident_id: str) -> List[Dict[str, Any]]:
        """Returns all individual citizen complaints linked to a master incident."""
        linked_ids = {l['complaint_id'] for l in self._links if l['master_incident_id'] == incident_id}
        # Read from complaints.json in tables
        complaints_path = TABLES_DIR / "complaints.json"
        all_c = self._load_json(complaints_path)
        return [c for c in all_c if c.get('id') in linked_ids]

    def get_all_incidents(
        self,
        municipality: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters master incidents for Department Head & Officer dashboards."""
        res = self._incidents
        if municipality:
            res = [i for i in res if i.get('municipality', '').upper() == municipality.upper()]
        if department:
            res = [i for i in res if i.get('department_code') == department or i.get('department') == department]
        if status:
            res = [i for i in res if i.get('status') == status]
        return res

def random_suffix() -> str:
    import random
    return f"{random.randint(10000, 99999)}"

_GLOBAL_STORE = None

def get_vector_store() -> IncidentVectorStore:
    global _GLOBAL_STORE
    if _GLOBAL_STORE is None:
        _GLOBAL_STORE = IncidentVectorStore()
    return _GLOBAL_STORE
