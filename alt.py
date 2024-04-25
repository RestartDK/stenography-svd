import numpy as np
from numpy.linalg import svd
from PIL import Image

# Encode algorithm using SVD
def encode(img, text):
	image = Image.open(img, "r")
	image = image.convert("RGB")

	# Step 1: Split the image into RGB components
	r, g, b = image.split()
	r_array, g_array, b_array = np.array(r, dtype=np.uint8), np.array(g, dtype=np.uint8), np.array(b, dtype=np.uint8)

	# Step 2: Perform SVD on each component (convert to float for SVD)
	U_r, S_r, Vt_r = svd(r_array.astype(float), full_matrices=False)
	U_g, S_g, Vt_g = svd(g_array.astype(float), full_matrices=False)
	U_b, S_b, Vt_b = svd(b_array.astype(float), full_matrices=False)

	# Step 3: Embed message into LSB
	binary_data = ''.join(format(ord(char), '08b') for char in text)
	idx = 0  # index for binary data
	rows, cols = r_array.shape

	# Define the stego-image arrays
	stego_r, stego_g, stego_b = np.copy(r_array), np.copy(g_array), np.copy(b_array)

	for i in range(rows):
			for j in range(cols):
					if idx + 8 <= len(binary_data):
							# Extract 8 bits and split them into 3 (R), 3 (G), and 2 bits (B)
							bits = binary_data[idx:idx + 8]
							r_bits, g_bits, b_bits = bits[:3], bits[3:6], bits[6:8]

							# Embed into LSBs of the RGB pixels
							stego_r[i, j] = (stego_r[i, j] & ~0b111) | int(r_bits, 2)
							stego_g[i, j] = (stego_g[i, j] & ~0b111) | int(g_bits, 2)
							stego_b[i, j] = (stego_b[i, j] & ~0b11) | int(b_bits, 2)

							idx += 8
					if idx >= len(binary_data):
							break
			if idx >= len(binary_data):
					break

	# Step 5: Convert arrays back to images and merge to form the stego image
	stego_r_img = Image.fromarray(np.uint8(stego_r))
	stego_g_img = Image.fromarray(np.uint8(stego_g))
	stego_b_img = Image.fromarray(np.uint8(stego_b))

	stego_image = Image.merge("RGB", (stego_r_img, stego_g_img, stego_b_img))
	new_img_name = input("Enter the name of new image(with extension) : ")
	stego_image.save(new_img_name, str(new_img_name.split(".")[1].upper()))


def decode():
  # Step 1: Load the encoded image and Split the image into RGB components
	img_path = input("Enter encoded image name (with extension): ")
	encoded_image = Image.open(img_path)
	encoded_image = encoded_image.convert("RGB")

	r, g, b = encoded_image.split()
	r_array = np.array(r, dtype=np.uint8)
	g_array = np.array(g, dtype=np.uint8)
	b_array = np.array(b, dtype=np.uint8)

	# Step 2: Extract bits according to the number of bits specified (Defined in the encode function)
	r_bits = extract_bits(r_array, 3)
	g_bits = extract_bits(g_array, 3)
	b_bits = extract_bits(b_array, 2)

	# Step 3: Merge the bits to reconstruct integers and the message
	message = reconstruct_message(r_bits, g_bits, b_bits)

	return message

def extract_bits(array, num_bits):
	"""Extract the least significant num_bits from each pixel in the array."""
 
	bit_mask = (1 << num_bits) - 1
	return array & bit_mask

def reconstruct_message(r_bits, g_bits, b_bits):
	"""Reconstruct the message from bits extracted from RGB components."""

	height, width = r_bits.shape
	message = ''
	for i in range(height):
			for j in range(width):
					# Combine bits to form the character byte
					byte = (r_bits[i, j] << 5) | (g_bits[i, j] << 2) | b_bits[i, j]
					if byte == 0:  # Assuming zero as a termination symbol
							return message
					message += chr(byte)
	return message

def main():
	a = int(
			input(
					":: Welcome to Steganography ::\n"
					"1. Encode\n2. Decode\n"
			)
	)
	if a == 1:
		img = input("Enter image name(with extension) : ")
		text = input("Enter text to be encoded : ")
		encode(img, text)
	elif a == 2:
		print("Decoded Word : " + decode())
	else:
		raise Exception("Enter correct input")

if __name__ == "__main__":
	main()