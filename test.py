import imagehash

def similarity(hash_list_1, hash_list_2):
    difference = []
    for hash1, hash2 in zip(hash_list_1, hash_list_2):
        hash1_hex= imagehash.hex_to_hash(hash1)
        hash2_hex = imagehash.hex_to_hash(hash2)
        difference.append(abs(hash1_hex - hash2_hex))

    difference_avg = (sum(difference) / len(difference)) / 255
    return (1 - difference_avg) * 100


# Full 
hash1 = ["97ffbffeafebaffbabfba3ef202f4237401354165c0c50145c047c1074007c00", "af9b76963deadad5e52e2a091dd864f6a2005809282e91f11ad16e0ad795a7f6", "95eb95eb91eb99da9dda9d1a3d1a3d1c3d1c3c1c3a1c7a147a146225626542e5"]


# Music 
hash2 = ["c218cd188f989d18d719f22331c332e732e735e739e742ef6a5c4ab46a346e1c", "99c272143f2e9a3bd544ed265b1d1f2b62b4d5429a9b671e2abb98c165602abd", "85eb85eb85db85da8dda8d9a8d9e8d1cac1cac1ca81cb81cba1caa9cea8ce2ad"]

# Instrument
hash3 = ["bbb383a183af50ef41ef43e345e7547e547e3d1c3c18bc58bc503e106c3061bc", "cabfcc7d8a21de7a8fa50f09afae4cb8482be43ef0be4068705abf9625411383", "9af392f392f392f192f192f192f192f192f392f190f290f3b072b072b072b132"]

similarity_precentage= similarity(hash1, hash3)
print(f"Similarity Percentage: {similarity_precentage}%")