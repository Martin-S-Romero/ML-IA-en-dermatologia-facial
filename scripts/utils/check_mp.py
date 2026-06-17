import sys
try:
    import mediapipe
    print(f"MediaPipe Version: {getattr(mediapipe, '__version__', 'unknown')}")
    print(f"MediaPipe File: {mediapipe.__file__}")
    print(f"Dir(mediapipe): {dir(mediapipe)}")
    
    try:
        import mediapipe.python
        print("✅ Imported mediapipe.python")
    except ImportError as e:
        print(f"❌ Failed mediapipe.python: {e}")

    try:
        import mediapipe.solutions
        print("✅ Imported mediapipe.solutions (direct)")
    except ImportError as e:
        print(f"❌ Failed mediapipe.solutions (direct): {e}")

    try:
        from mediapipe.python.solutions import face_mesh
        print("✅ Imported face_mesh from python.solutions")
    except ImportError as e:
        print(f"❌ Failed face_mesh from python.solutions: {e}")

except ImportError as e:
    print(f"❌ Failed to import mediapipe: {e}")
