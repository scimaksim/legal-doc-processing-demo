"""Architecture diagram for Legal Document Intelligence Platform on Databricks."""
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.programming.framework import React
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.generic.database import SQL
import os

ICONS = "/Users/maksim.nikiforov/.claude/plugins/cache/fe-vibe/fe-workflows/1.2.9/skills/fe-architecture-diagram/resources/icons"

with Diagram(
    "Legal Document Intelligence Platform on Databricks",
    show=False,
    filename="/Users/maksim.nikiforov/legal-doc-processing-demo/docs/architecture",
    outformat="png",
    direction="LR",
    graph_attr={
        "splines": "polyline",
        "nodesep": "0.8",
        "ranksep": "1.8",
        "pad": "0.8",
        "fontsize": "18",
        "bgcolor": "white",
        "dpi": "150",
        "fontname": "Helvetica",
        "labeljust": "c",
    },
    node_attr={
        "fontsize": "11",
        "fontname": "Helvetica",
    },
    edge_attr={
        "fontsize": "9",
        "fontname": "Helvetica",
        "color": "#475569",
    },
):

    # === DATA SOURCES ===
    with Cluster("Document Sources", graph_attr={"bgcolor": "#fef3c7", "style": "rounded", "pencolor": "#d97706", "fontsize": "13", "fontname": "Helvetica Bold"}):
        subpoenas = Storage("Subpoenas\n& Legal Filings")
        invoices = Storage("Outside Counsel\nInvoices")
        contracts = Storage("Contracts\n& Agreements")
        regulatory = Storage("Regulatory\nFilings")

    # === DATABRICKS PLATFORM ===
    with Cluster("Databricks Lakehouse", graph_attr={"bgcolor": "#eff6ff", "style": "rounded", "pencolor": "#2563eb", "fontsize": "14", "fontname": "Helvetica Bold"}):

        # Ingestion
        with Cluster("Ingestion", graph_attr={"bgcolor": "#dbeafe", "style": "rounded", "pencolor": "#3b82f6", "fontsize": "12"}):
            volumes = Custom("UC Volumes\n(Raw PDFs)", f"{ICONS}/databricks/unity_catalog.png")

        # AI Processing
        with Cluster("AI Processing", graph_attr={"bgcolor": "#fae8ff", "style": "rounded", "pencolor": "#a855f7", "fontsize": "12"}):
            parse = Custom("ai_document_parse()\nPDF → Elements", f"{ICONS}/databricks/model_serving.png")
            extract = Custom("ai_query()\nKey Info Extraction", f"{ICONS}/databricks/model_serving.png")
            txt2sql = Custom("ai_query()\nText-to-SQL", f"{ICONS}/databricks/model_serving.png")

        # Storage
        with Cluster("Delta Tables (Unity Catalog)", graph_attr={"bgcolor": "#dcfce7", "style": "rounded", "pencolor": "#16a34a", "fontsize": "12"}):
            parsed_tbl = Custom("parsed_documents", f"{ICONS}/databricks/delta_lake.png")
            elements_tbl = Custom("document_elements", f"{ICONS}/databricks/delta_lake.png")
            keyinfo_tbl = Custom("extracted_key_info", f"{ICONS}/databricks/delta_lake.png")

        # Governance
        uc = Custom("Unity Catalog\nGovernance & Lineage", f"{ICONS}/databricks/unity_catalog.png")

    # === APPLICATION ===
    with Cluster("Databricks App", graph_attr={"bgcolor": "#fef9c3", "style": "rounded", "pencolor": "#ca8a04", "fontsize": "13", "fontname": "Helvetica Bold"}):
        app = Custom("React + FastAPI\nSQL Statements API", f"{ICONS}/databricks/workspace.png")
        warehouse = Custom("Serverless\nSQL Warehouse", f"{ICONS}/databricks/sql_warehouse.png")

    # === USERS ===
    user = User("Legal Teams\n& Analysts")

    # === FLOW ===
    # Sources -> Volumes
    subpoenas >> Edge(color="#d97706") >> volumes
    invoices >> Edge(color="#d97706") >> volumes
    contracts >> Edge(color="#d97706") >> volumes
    regulatory >> Edge(color="#d97706") >> volumes

    # Volumes -> Parse
    volumes >> Edge(label="Binary PDFs", color="#3b82f6") >> parse

    # Parse -> Tables
    parse >> Edge(label="Structured\nElements", color="#a855f7") >> parsed_tbl
    parsed_tbl >> Edge(color="#16a34a") >> elements_tbl

    # Extract
    elements_tbl >> Edge(label="Full Text", color="#a855f7") >> extract
    extract >> Edge(label="Parties, Dates\n$, Risks", color="#a855f7") >> keyinfo_tbl

    # Governance
    parsed_tbl >> Edge(style="dashed", color="#16a34a") >> uc
    elements_tbl >> Edge(style="dashed", color="#16a34a") >> uc
    keyinfo_tbl >> Edge(style="dashed", color="#16a34a") >> uc

    # App queries
    keyinfo_tbl >> Edge(color="#ca8a04") >> warehouse
    elements_tbl >> Edge(color="#ca8a04") >> warehouse
    warehouse >> Edge(color="#ca8a04") >> app

    # Text-to-SQL
    app >> Edge(label="NL Query", color="#a855f7", style="dashed") >> txt2sql
    txt2sql >> Edge(label="Generated SQL", color="#a855f7", style="dashed") >> warehouse

    # User
    user >> Edge(color="#475569") >> app
