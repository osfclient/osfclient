import os


def validate_containing_folder(containing_folder):
    """Validate that the containing folder exists, and that the user has permission to access it"""
    if containing_folder and os.path.isdir(containing_folder):
        osf_path = os.path.join(containing_folder, "OSF")
        # Verify that there is no file with same name as storage folder, and that user can create files here
        return (not os.path.isfile(osf_path)) and os.access(containing_folder, os.W_OK | os.X_OK)
    else:
        return False
