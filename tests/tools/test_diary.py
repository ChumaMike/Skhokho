def test_diary_persistence(client, auth, app):
    """QA: Can I write thoughts to the Diary?"""
    auth.register()
    auth.login()

    # 1. Write an entry
    client.post('/tools/diary', data={
        'entry_type': 'Engineering Win',
        'content': 'Tests are fixed.'
    }, follow_redirects=True)

    # 2. Verify it appears
    response = client.get('/tools/diary')
    assert b"Engineering Win" in response.data