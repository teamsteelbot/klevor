import streamlit as st
from PIL.Image import Image

from camera.images_queue import ImagesQueue


class RealtimeTrackerApp:
    """
    A class to represent a real-time tracker application.

    It's only used on debug mode for testing new features, but not on competition.

    This class is intended to be used as a Streamlit app for tracking real-time data.
    """
    __images_queue = None
    __capture_image_event = None
    __image_container_left = None
    __image_container_right = None
    __original_image_container = None
    __model_g_image_container = None
    __model_m_image_container = None
    __model_r_image_container = None

    def __init__(self, images_queue: ImagesQueue=None):
        """
        Initializes the RealtimeTrackerApp instance.
        """
        if not isinstance(images_queue, ImagesQueue):
            raise TypeError("images_queue must be an instance of ImagesQueue")
        self.__images_queue = images_queue

        # Get the capture image event from the images queue
        self.__capture_image_event = self.__images_queue.get_capture_image_event()

        # Set the title and description of the Streamlit app
        st.title("Realtime Tracker App")
        st.write("This is a placeholder for the real-time tracker functionality.")

        # Create a container for the original image display and the three different images inferences
        self.__image_container_left, self.__image_container_right = st.columns(2)
        self.__original_image_container = self.__image_container_left.container("Original Image")
        self.__model_g_image_container = self.__image_container_right.container("Model G Image")
        self.__model_m_image_container = self.__image_container_right.container("Model M Image")
        self.__model_r_image_container = self.__image_container_right.container("Model R Image")

    def update_original(self, image: Image):
        """
        Updates the original image in the Streamlit app.
        """
        self.__original_image_container.image(image, caption="Original Image", use_column_width=True)

    def update_model_g_image_container(self, image: Image):
        """
        Updates the model G inference image in the Streamlit app.
        """
        self.__model_g_image_container.image(image, caption="Inference 1", use_column_width=True)

    def update_model_m_image_container(self, image: Image):
        """
        Updates the model M inference image in the Streamlit app.
        """
        self.__model_m_image_container.image(image, caption="Inference 2", use_column_width=True)

    def update_model_r_image_container(self, image: Image):
        """
        Updates the model R inference image in the Streamlit app.
        """
        self.__model_r_image_container.image(image, caption="Inference 3", use_column_width=True)

    def run(self):
        """
        Runs the Streamlit app.

        This method should contain the logic to start the Streamlit app.
        """

if __name__ == "__main__":
    # Initialize the RealtimeTrackerApp
    realtime_tracker_app = RealtimeTrackerApp()