# %%
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from data import load_got
from PIL import Image

DATA_PATH = os.path.join(os.getcwd(), "data")
NODE_PATH = os.path.join(DATA_PATH, "got_nodes.csv")
EDGE_PATH = os.path.join(DATA_PATH, "got_edges.csv")
FILE_PATH_FOR_IMAGE_URLS = "data/image_urls.csv"
FILE_PATH_FOR_IMAGES = "assets/portrait_images"


def create_url_from_node_name(node_name):
    node_name = node_name.replace("-", "_")
    url = f"""https://gameofthrones.fandom.com/wiki/{node_name}"""
    return url


def create_wiki_urls(nodes):
    """
    Load the data into pandas dataframes
    """
    nodes["url"] = nodes["id"].apply(create_url_from_node_name)

    return nodes


def get_image_url(url):
    try:
        # Retrieve the HTML content
        response = requests.get(url)
        html_content = response.text

        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the section containing the image
        image_section = soup.find("figure", {"class": "pi-item pi-image"})

        # Extract the image URL
        image_url = image_section.find("img")["src"]

        return image_url
    except AttributeError:
        print(f"AttributeError occurred for the following URL: {url}")
        print("Returning an empty string.")
        return ""


def add_image_urls_to_nodes_file(nodes):
    nodes["image_url"] = None
    for id, row in nodes.iterrows():
        url = row["url"]
        print(f"Processing url: {url}")
        image_url = get_image_url(url)
        nodes.loc[id, "image_url"] = image_url

    return nodes


def download_images(nodes):
    for id, row in nodes.iterrows():
        image_url = row["image_url"]
        node_id = row["id"]
        file_name = os.path.join(FILE_PATH_FOR_IMAGES, f"{node_id}.png")
        print(f"Processing Node id: {node_id}")
        if image_url != "" and not os.path.exists(file_name):
            try:
                response = requests.get(image_url)
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Save the image content to a file
                    with open(file_name, "wb") as file:
                        file.write(response.content)
                    print("Image downloaded successfully!")
                else:
                    print(
                        f"Failed to download the image. response.status_code = {response.status_code}"
                    )
            except:
                print("Failed to download the image. requests.get(image_url) failed")


# %%
def crop_images(directory, fraction_to_keep):
    """
    Cropping of a part of the bottom of images in the directory to make the faces in the image become more in the center.
    This function was written by chatGPT with no edits required!!! :D
    """
    # Get a list of all files in the directory
    file_list = os.listdir(directory)

    # Filter the list to include only PNG files
    png_files = [f for f in file_list if f.endswith(".png")]

    # Process each PNG file
    for file_name in png_files:
        # Open the image
        image_path = os.path.join(directory, file_name)
        image = Image.open(image_path)

        # Get the dimensions of the image
        width, height = image.size

        # Calculate the crop dimensions
        crop_height = int(height * fraction_to_keep)  # Keep 90% of the original height

        # Crop the image
        cropped_image = image.crop((0, 0, width, crop_height))

        # Save the cropped image, overwriting the original file
        cropped_image.save(image_path)

        # Close the image
        image.close()

    print("Cropping complete!")


if __name__ == "__main__":
    nodes, _ = load_got()
    nodes = create_wiki_urls(nodes)
    nodes = add_image_urls_to_nodes_file(nodes)
    nodes.to_csv(NODE_PATH, index=False)
    download_images(nodes)
    # Call the function to crop the images
    crop_images(FILE_PATH_FOR_IMAGES, fraction_to_keep=0.7)
