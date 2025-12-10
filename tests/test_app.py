"""
Tests for the Mergington High School API
"""

import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that GET /activities contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Basketball Team" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_returns_200(self):
        """Test signing up a new student returns 200"""
        response = client.post(
            "/activities/Basketball Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_new_student_returns_success_message(self):
        """Test signup returns success message"""
        response = client.post(
            "/activities/Art Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Art Club" in data["message"]

    def test_signup_duplicate_student_returns_400(self):
        """Test signing up the same student twice returns 400"""
        email = "duplicate@mergington.edu"
        activity = "Drama Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_invalid_activity_returns_404(self):
        """Test signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds participant to the activity"""
        email = "verify@mergington.edu"
        activity = "Math Club"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get updated participant count
        response2 = client.get("/activities")
        updated_count = len(response2.json()[activity]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in response2.json()[activity]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_returns_200(self):
        """Test unregistering an existing student returns 200"""
        email = "unregister_test@mergington.edu"
        activity = "Debate Team"
        
        # First sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """Test unregister returns success message"""
        email = "unregister_msg@mergington.edu"
        activity = "Soccer Club"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_nonexistent_student_returns_400(self):
        """Test unregistering a student not in the activity returns 400"""
        response = client.delete(
            "/activities/Gym Class/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_invalid_activity_returns_404(self):
        """Test unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister actually removes participant from the activity"""
        email = "verify_removal@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get participant count before unregister
        response1 = client.get("/activities")
        count_before = len(response1.json()[activity]["participants"])
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Get participant count after unregister
        response2 = client.get("/activities")
        count_after = len(response2.json()[activity]["participants"])
        
        assert count_after == count_before - 1
        assert email not in response2.json()[activity]["participants"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 303, 307, 308]
        assert "/static" in response.headers["location"]
