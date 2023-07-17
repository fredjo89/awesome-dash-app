# awesome-dash-app

This repository contains code that creates a webpage with a dashboard for a game of thrones character network. 
Core functionality of the dashboard is to allow the user to search and filter in the graph, e.g. 
- Search for a character and its closest neighborhood
- Filter characters based on its screentime
- Filter edges/relations based on its strength

The network visualization is interactive, and delete or expand a node's neighborhood by clicking on it. 
The user can also choose to open a character's wiki webpage by clicking on the node. 

The dashboard is created using dash and visdcc as core components, where dash is used to create the web application and visdcc to create the network visualization. 
The creation of the dashboard was highly inspored by [jaal](https://github.com/imohitmayank/jaal)

## Installation

## File Structure

- `app.py`
    - Runs the app
    - Depends on ?? and ??
- `layout.py`
    - Defines the layout of the dashboard
    - Depends on 
- `callbacks.py`
    - Defines the user interactions, i.e. the callback functions used by the dashboard. 
- `data.py`
    - Loads the data and defines all operations on the data that is the backend for the data shown on the dashboard
- The `data`- folder
    - Contains the raw data for the network in two csv-files; one that holds the nodes and one the edges. 
- The `assets`- folder
    - Holds all images used by the dashboard, in additon to the file `styles-css` used to define the styles of the different components of the dashboard. 
- `download_portraits.py`
    - A python-script that downloads and crops potrait-images of the characters in the network. These images are used in the network visualization. The result of running this script is all the images in `assets/portrait_images`, and it's not neccecary to run it unless these images for some reason disapear or require modification. 

