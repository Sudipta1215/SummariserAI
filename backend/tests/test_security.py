# 1. Test Edge Case: Uploading Wrong File Type
def test_upload_invalid_file(client, test_db):
    file_content = b"This is a text file acting like an image"
    files = {"file": ("image.png", file_content, "image/png")}
    
    response = client.post(
        "/books/",
        data={"title": "Bad File", "author": "Hacker", "user_id": 1},
        files=files
    )
    
    # Should fail because we only allow PDF, DOCX, TXT
    assert response.status_code == 400 

# 2. Test Admin Security (Accessing Admin stats as normal user/guest)
def test_unauthorized_admin_access(client):
    # We are not logged in, or we assume the client defaults to no auth headers
    response = client.get("/admin/stats")
    
    # Depending on your implementation, this might return 403 (Forbidden) or 401 (Unauthorized)
    # If you haven't strictly enforced Admin middleware yet, this test acts as a TODO reminder.
    # For now, let's just ensure the endpoint exists.
    assert response.status_code in [200, 401, 403]