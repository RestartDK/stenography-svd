import numpy as np
from numpy.linalg import svd
from PIL import Image

def encode(img_path, text):
    # Load image and convert to RGB
    image = Image.open(img_path)
    image = image.convert("RGB")

    # Split the image into RGB components
    r, g, b = image.split()
    r_array = np.array(r, dtype=float)
    g_array = np.array(g, dtype=float)
    b_array = np.array(b, dtype=float)

    # Convert text to binary data
    binary_data = ''.join(format(ord(char), '08b') for char in text)

    # Perform SVD on each component
    U_r, S_r, Vt_r = svd(r_array, full_matrices=False)
    U_g, S_g, Vt_g = svd(g_array, full_matrices=False)
    U_b, S_b, Vt_b = svd(b_array, full_matrices=False)

    # Embed binary data into the least significant singular values
    embed_into_singular_values(S_r, binary_data)
    embed_into_singular_values(S_g, binary_data)
    embed_into_singular_values(S_b, binary_data)

    # Reconstruct the image using the modified singular values
    new_r = np.dot(U_r, np.dot(np.diag(S_r), Vt_r))
    new_g = np.dot(U_g, np.dot(np.diag(S_g), Vt_g))
    new_b = np.dot(U_b, np.dot(np.diag(S_b), Vt_b))

    # Convert arrays back to images and merge to form the stego image
    stego_image = Image.merge("RGB", [
        Image.fromarray(np.clip(channel, 0, 255).astype(np.uint8))
        for channel in (new_r, new_g, new_b)
    ])
    new_img_name = input("Enter the name of new image(with extension) : ")
    stego_image.save(new_img_name, str(new_img_name.split(".")[1].upper()))

def embed_into_singular_values(S, binary_data):
    """ Embed binary data into singular values starting from the least significant. """
    idx = 0
    for i in range(len(S)-1, len(S)-11, -1):  # Modify last 10 singular values
        if idx < len(binary_data):
            # Embed by adding a small fraction to the singular value
            S[i] += 0.05 if binary_data[idx] == '1' else 0.01  # Smaller change for '0' to differentiate
            idx += 1
        else:
            break

def decode(encoded_img_path):
    # Load the stego image and convert to RGB
    image = Image.open(encoded_img_path)
    image = image.convert("RGB")

    # Split the image into RGB components
    r, g, b = image.split()
    r_array = np.array(r, dtype=float)
    g_array = np.array(g, dtype=float)
    b_array = np.array(b, dtype=float)

    # Perform SVD on each component
    U_r, S_r, Vt_r = svd(r_array, full_matrices=False)
    U_g, S_g, Vt_g = svd(g_array, full_matrices=False)
    U_b, S_b, Vt_b = svd(b_array, full_matrices=False)

    # Extract the binary data from the least significant singular values
    binary_message = extract_message_from_singular_values(S_r)
    binary_message += extract_message_from_singular_values(S_g)
    binary_message += extract_message_from_singular_values(S_b)

    # Convert binary data to string
    message = binary_to_string(binary_message)
    return message

def extract_message_from_singular_values(S):
    """ Extract binary data embedded in the least significant singular values. """
    binary_data = ''
    for value in S[-10:]:  # Assume last 10 values were modified
        # Calculate the fraction part and convert to binary
        fraction = value - int(value)
        if fraction > 0.045:  # Assume a bit of '1' was added as 0.05
            binary_data += '1'
        else:
            binary_data += '0'
    return binary_data

def binary_to_string(binary_data):
    """ Convert binary string to human-readable text. """
    message = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8:
            continue
        message += chr(int(byte, 2))
    return message

def main():
    a = int(input(":: Welcome to Steganography ::\n1. Encode\n2. Decode\n"))
    if a == 1:
        img = input("Enter image name(with extension) : ")
        text = input("Enter text to be encoded : ")
        encode(img, text)
    elif a == 2:
      encoded_img_path = input("Enter encoded image name (with extension): ")
      print(f"Decoded message: {decode(encoded_img_path)}")
    else:
        raise Exception("Enter correct input")

if __name__ == "__main__":
    main()
