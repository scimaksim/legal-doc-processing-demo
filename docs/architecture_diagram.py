"""Architecture diagram for Legal Document Intelligence Platform on Databricks."""
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.generic.storage import Storage
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
        "nodesep": "0.7",
        "ranksep": "1.6",
        "pad": "0.8",
        "fontsize": "18",
        "bgcolor": "white",
        "dpi": "150",
        "fontname": "Helvetica",
        "labeljust": "c",
    },
    node_attr={
        "fontsize": "10",
        "fontname": "Helvetica",
    },
    edge_attr={
        "fontsize": "8",
        "fontname": "Helvetica",
        "color": "#475569",
    },
):

    # === DATA SOURCES ===
    with Cluster("Document Sources", graph_attr={"bgcolor": "#fef3c7", "style": "rounded", "pencolor": "#d97706", "fontsize": "13", "fontname": "Helvetica Bold"}):
        subpoenas = Storage("Subpoenas")
        invoices = Storage("Outside Counsel\nInvoices")
        contracts = Storage("Contracts\n& Agreements")
        regulatory = Storage("Regulatory\nFilings")

    # === DATABRICKS PLATFORM ===
    with Cluster("Databricks Lakehouse", graph_attr={"bgcolor": "#eff6ff", "style": "rounded", "pencolor": "#2563eb", "fontsize": "14", "fontname": "Helvetica Bold"}):

        # Ingestion
        with Cluster("Ingestion", graph_attr={"bgcolor": "#dbeafe", "style": "rounded", "pencolor": "#3b82f6", "fontsize": "12"}):
            volumes = Custom("UC Volumes\n(Raw PDFs)", f"{ICONS}/databricks/unity_catalog.png")

        # AI Processing
        with Cluster("AI Processing (Foundation Models)", graph_attr={"bgcolor": "#fae8ff", "style": "rounded", "pencolor": "#a855f7", "fontsize": "12"}):
            parse = Custom("ai_document_parse()\nPDF → Elements", f"{ICONS}/databricks/model_serving.png")
            extract = Custom("ai_query()\nSpecialized Extraction", f"{ICONS}/databricks/model_serving.png")
            genie = Custom("Genie\nConversation API", f"{ICONS}/databricks/model_serving.png")

        # Delta Storage
        with Cluster("Delta Tables (Unity Catalog)", graph_attr={"bgcolor": "#dcfce7", "style": "rounded", "pencolor": "#16a34a", "fontsize": "12"}):
            parsed_tbl = Custom("parsed_documents\ndocument_elements", f"{ICONS}/databricks/delta_lake.png")
            keyinfo_tbl = Custom("extracted_key_info\nextracted_subpoenas", f"{ICONS}/databricks/delta_lake.png")
            inv_reg_tbl = Custom("extracted_invoices\nextracted_regulatory", f"{ICONS}/databricks/delta_lake.png")

        # Lakebase
        with Cluster("Lakebase (OLTP)", graph_attr={"bgcolor": "#fef9c3", "style": "rounded", "pencolor": "#ca8a04", "fontsize": "12"}):
            lakebase = Custom("subpoena_tracking\ninvoice_reviews", f"{ICONS}/databricks/delta_lake.png")

        # Governance
        uc = Custom("Unity Catalog\nGovernance & Lineage", f"{ICONS}/databricks/unity_catalog.png")

        # AI/BI Dashboard
        with Cluster("AI/BI Dashboard", graph_attr={"bgcolor": "#e0e7ff", "style": "rounded", "pencolor": "#4f46e5", "fontsize": "12"}):
            aibi = Custom("Matter Overview\nBilling Audit\nCompliance & Risk", f"{ICONS}/databricks/sql_warehouse.png")

    # === APPLICATION ===
    with Cluster("Databricks App (React + FastAPI)", graph_attr={"bgcolor": "#f1f5f9", "style": "rounded", "pencolor": "#64748b", "fontsize": "13", "fontname": "Helvetica Bold"}):
        app = Custom("Document Browser\nKey Insights\nAsk (Genie)", f"{ICONS}/databricks/workspace.png")
        app_ops = Custom("Subpoena Tracker\nInvoice Auditor\nRegulatory View", f"{ICONS}/databricks/workspace.png")
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

    # Extract
    parsed_tbl >> Edge(label="Full Text", color="#a855f7") >> extract
    extract >> Edge(label="Contracts, Subpoenas\nInvoices, Regulatory", color="#a855f7") >> keyinfo_tbl
    extract >> Edge(color="#a855f7") >> inv_reg_tbl

    # Governance
    parsed_tbl >> Edge(style="dashed", color="#16a34a") >> uc
    keyinfo_tbl >> Edge(style="dashed", color="#16a34a") >> uc
    inv_reg_tbl >> Edge(style="dashed", color="#16a34a") >> uc
    lakebase >> Edge(style="dashed", color="#ca8a04") >> uc

    # App queries - Delta tables to warehouse
    keyinfo_tbl >> Edge(color="#64748b") >> warehouse
    inv_reg_tbl >> Edge(color="#64748b") >> warehouse

    # Lakebase to warehouse
    lakebase >> Edge(label="OLTP\nWorkflows", color="#ca8a04") >> warehouse

    # Warehouse to app and AI/BI Dashboard
    warehouse >> Edge(color="#64748b") >> app
    warehouse >> Edge(color="#64748b") >> app_ops
    warehouse >> Edge(color="#4f46e5") >> aibi

    # AI/BI Dashboard embedded in app
    aibi >> Edge(label="Embedded", color="#4f46e5", style="dashed") >> app

    # Genie
    app >> Edge(label="NL Query", color="#a855f7", style="dashed") >> genie
    genie >> Edge(label="Generated SQL", color="#a855f7", style="dashed") >> warehouse

    # User
    user >> Edge(color="#475569") >> app
    user >> Edge(color="#475569") >> app_ops
