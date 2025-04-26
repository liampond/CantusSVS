def validate_ds(ds_dict):
    """
    Ensure that the DS dictionary has all required fields
    and that fields have the correct types.
    """
    required_fields = ["ph_seq", "ph_num", "note_seq", "note_dur_seq", "is_slur_seq", "input_type"]
    
    for field in required_fields:
        if field not in ds_dict:
            raise ValueError(f"Missing required field '{field}' in DS file.")
    
    if not isinstance(ds_dict["ph_seq"], str):
        raise TypeError("Field 'ph_seq' must be a string.")
    if not isinstance(ds_dict["ph_num"], int):
        raise TypeError("Field 'ph_num' must be an integer.")
    if not isinstance(ds_dict["note_seq"], str):
        raise TypeError("Field 'note_seq' must be a string.")
    if not isinstance(ds_dict["note_dur_seq"], str):
        raise TypeError("Field 'note_dur_seq' must be a string.")
    if not isinstance(ds_dict["is_slur_seq"], str):
        raise TypeError("Field 'is_slur_seq' must be a string.")
    if not isinstance(ds_dict["input_type"], str):
        raise TypeError("Field 'input_type' must be a string.")
