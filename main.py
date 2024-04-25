import numpy as np
import imageio.v2 as imageio
from numpy.linalg import svd

class Steganographer:
    def __init__(self, image_path):
        self.image_path = image_path
        # Load the image
        self.image = imageio.imread(image_path)
        # Check if the image has more than 3 channels (e.g., RGBA), and discard the alpha channel
        if self.image.ndim == 3 and self.image.shape[2] == 4:
            self.image = self.image[:, :, :3]  # Keep only the first three channels (RGB)

    def embed(self, message):
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        idx = 0
        rows, cols, _ = self.image.shape

        for i in range(rows):
            for j in range(cols):
                if idx < len(binary_message):
                    U, S, Vt = svd(self.image[i, j].astype(float).reshape((3, 1)), full_matrices=False)
                    # Embedding data into least significant bit of the smallest singular value
                    S[-1] = int(S[-1]) & ~1 | int(binary_message[idx], 2)
                    idx += 1

                    # Reconstruct the pixel
                    new_pixel = np.dot(U, np.dot(np.diag(S.flatten()), Vt)).astype(np.uint8).flatten()
                    self.image[i, j] = np.clip(new_pixel, 0, 255)

                if idx >= len(binary_message):
                    break
            if idx >= len(binary_message):
                break

        imageio.imwrite(self.image_path.replace('.png', '_steg.png'), self.image)
        print(f"Message embedded and image saved as {self.image_path.replace('.png', '_steg.png')}")

    def extract(self):
        binary_message = ''
        rows, cols, _ = self.image.shape
        for i in range(rows):
            for j in range(cols):
                U, S, Vt = svd(self.image[i, j].astype(float).reshape((3, 1)), full_matrices=False)
                lsb = int(S[-1]) & 1
                binary_message += str(lsb)

                if len(binary_message) % 8 == 0:
                    # Check for termination character
                    if int(binary_message[-8:], 2) == 0:
                        break
            if int(binary_message[-8:], 2) == 0:
                break

        message = ''.join([chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message)-8, 8)])
        return message

def main():
    print("Welcome to the SVD Steganography Tool")
    choice = input("Would you like to (e)mbed or (d)ecode a message? ")
    
    if choice.lower() == 'e':
        img_path = input("Enter the path to the image: ")
        message = input("Enter the message to embed: ")
        steg = Steganographer(img_path)
        steg.embed(message)
    elif choice.lower() == 'd':
        img_path = input("Enter the path to the steganographic image: ")
        steg = Steganographer(img_path)
        message = steg.extract()
        print("Extracted message:", message)
    else:
        print("Invalid choice. Please select 'e' to embed or 'd' to decode.")

if __name__ == "__main__":
    main()
