import numpy as np
import imageio.v2 as imageio
from numpy.linalg import svd

class Steganographer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = imageio.imread(image_path)
        if self.image.ndim == 3 and self.image.shape[2] == 4:
            self.image = self.image[:, :, :3]  # Discard alpha channel if present

    def embed(self, message):
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        idx = 0
        rows, cols, _ = self.image.shape

        # Split the image into RGB components
        r = self.image[:, :, 0]
        g = self.image[:, :, 1]
        b = self.image[:, :, 2]

        # Prepare modified RGB channels
        r_mod = r.copy().astype(float)
        g_mod = g.copy().astype(float)
        b_mod = b.copy().astype(float)

        # Embed message by iterating in blocks of 4x4
        for i in range(0, rows, 4):
            for j in range(0, cols, 4):
                if idx < len(binary_message):
                    # Handle RGB blocks
                    for color, color_mod in [(r, r_mod), (g, g_mod), (b, b_mod)]:
                        block = color[i:i+4, j:j+4].astype(float)
                        U, S, Vt = svd(block, full_matrices=False)
                        S_flat = S.flatten()
                        for s_index in range(len(S_flat)):
                            if idx < len(binary_message):
                                S_flat[s_index] = int(S_flat[s_index]) & ~1 | int(binary_message[idx], 2)
                                idx += 1
                        new_block = U @ np.diag(S_flat) @ Vt
                        color_mod[i:i+4, j:j+4] = new_block

                if idx >= len(binary_message):
                    break
            if idx >= len(binary_message):
                break

        # Recombine the RGB components and save the modified image
        modified_image = np.stack((r_mod, g_mod, b_mod), axis=2).astype(np.uint8)
        imageio.imwrite(self.image_path.replace('.png', '_steg.png'), modified_image)
        print(f"Message embedded and image saved as {self.image_path.replace('.png', '_steg.png')}")

    def extract(self):
        rows, cols, _ = self.image.shape
        binary_message = ''

        # Split the image into RGB components
        r = self.image[:, :, 0]
        g = self.image[:, :, 1]
        b = self.image[:, :, 2]

        # Extract message by iterating in blocks of 4x4
        for i in range(0, rows, 4):
            for j in range(0, cols, 4):
                # Handle RGB blocks
                for color in [r, g, b]:
                    block = color[i:i+4, j:j+4].astype(float)
                    U, S, Vt = svd(block, full_matrices=False)
                    S_flat = S.flatten()
                    for s_val in S_flat:
                        lsb = int(s_val) & 1
                        binary_message += str(lsb)
                        if len(binary_message) % 8 == 0 and int(binary_message[-8:], 2) == 0:
                            break
                if int(binary_message[-8:], 2) == 0:
                    break
            if int(binary_message[-8:], 2) == 0:
                break

        message = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message) - 8, 8))
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
