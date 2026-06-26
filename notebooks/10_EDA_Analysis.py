import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os

warnings.filterwarnings("ignore")

# Create folder for exported charts
os.makedirs("reports/charts", exist_ok=True)

print("✅ All libraries loaded")
