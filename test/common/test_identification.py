from airembr.sdk.common.identification import generate_pk, generate_triplet_id

def test_generate_pk():
    pk = generate_pk("User", "123")
    assert isinstance(pk, str)
    assert len(pk) == 32 # MD5 hex length
    
    # Verify deterministic
    assert pk == generate_pk("User", "123")
    # Verify different for different inputs
    assert pk != generate_pk("User", "124")
    assert pk != generate_pk("Project", "123")

def test_generate_triplet_id():
    tid = generate_triplet_id("actor1", "likes", "object1")
    assert isinstance(tid, str)
    assert len(tid) == 32
    
    # Verify deterministic
    assert tid == generate_triplet_id("actor1", "likes", "object1")
    # Verify different for different inputs
    assert tid != generate_triplet_id("actor2", "likes", "object1")
