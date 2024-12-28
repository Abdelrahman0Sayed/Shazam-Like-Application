def hex_to_binary(hex_hash):
    # Convert the hexadecimal string to a binary string
    return bin(int(hex_hash, 16))[2:].zfill(len(hex_hash) * 4)  # Ensure leading zeros are included

def hamming_distance(binary_hash1, binary_hash2):
    # Calculate the number of differing bits
    return sum(c1 != c2 for c1, c2 in zip(binary_hash1, binary_hash2))

def similarity_percentage(hamming_dist, hash_length):
    # Compute similarity percentage
    return 100 * (1 - hamming_dist / hash_length)

# Example hashes (in hexadecimal format)
hash1 = "6a3606ea5b131514d7555e8db66e20124701bd4b911af20bccb9aec1df1d306e4f8ab653bbc4d213405a8b96f4bb2cdbd48e08a2c4956bfc3f3c4c7793832c5a"
hash2 = "f8017702aeb8b7c499d9140968afe513c660dcee5205ef0ae75de657e93d6c0513af14fa43fe8af53906cafb4704dc8037dd687fa316834d4ae832ff2c2b8e42"

# Convert hex hashes to binary
binary_hash1 = hex_to_binary(hash1)
binary_hash2 = hex_to_binary(hash2)

# Ensure both binary hashes have the same length
hash_length = len(binary_hash1)

# Compute Hamming distance
distance = hamming_distance(binary_hash1, binary_hash2)

# Compute similarity percentage
similarity = similarity_percentage(distance, hash_length)  # Since each hex digit represents 4 bits

print(f"Hamming Distance: {distance}")
print(f"Similarity Percentage: {similarity}%")
