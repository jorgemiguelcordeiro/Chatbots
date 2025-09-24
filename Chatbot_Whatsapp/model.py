# 1 - Imports and Basic Setup

import os  #systems operations, like env variables and paths
import logging #lets the app output info on what is happening - helpful for debugging
import requests # - for http requests
import chromadb #vector database for storing and search embedding vectors from documents
from chromadb.utils import embedding_functions #tools for embedding text
from sentence_transformers import SentenceTransformer #embedding model for searching similarity
from typing import List #Typing help for Python, defines that certain variables are lists.

# Logger setup

logger = logging.getLogger("ingestion") #Sets up logging so you get timestamped messages, showing what the program’s doing (like adding docs, warnings).
if not logger.handlers: #Only creates a handler if it doesn’t exist already.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# API Key and Models
