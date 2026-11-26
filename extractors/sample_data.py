"""
Sample BW/4HANA System Metadata Repository Mock
Provides realistic metadata structures for testing T0-T12 tools.
"""

SAMPLE_BW_METADATA = {
    "source_systems": [
        {"tech_name": "S4HCLNT100", "object_type": "SOURCE_SYSTEM", "description": "S/4HANA Core ERP System"}
    ],
    "datasources": [
        {
            "tech_name": "DS_SALES_HEADER",
            "object_type": "DATASOURCE",
            "source_system": "S4HCLNT100",
            "description": "Sales Document Header Data",
            "fields": [
                {"name": "VBELN", "type": "CHAR", "length": 10, "is_key": True},
                {"name": "ERDAT", "type": "DATS", "length": 8},
                {"name": "KUNNR", "type": "CHAR", "length": 10},
                {"name": "NETWR", "type": "DEC", "length": 15, "decimals": 2},
                {"name": "WAERK", "type": "CUKY", "length": 5}
            ]
        }
    ],
    "infoobjects": [
        {
            "tech_name": "0CUSTOMER",
            "object_type": "INFOOBJECT",
            "io_type": "CHA", # Characteristic
            "description": "Customer Number",
            "datatype": "CHAR",
            "length": 10,
            "has_attributes": True,
            "has_texts": True,
            "attributes": ["0COUNTRY", "0REGION"],
            "compounding": []
        },
        {
            "tech_name": "0COUNTRY",
            "object_type": "INFOOBJECT",
            "io_type": "CHA",
            "description": "Country Key",
            "datatype": "CHAR",
            "length": 3,
            "has_attributes": False,
            "has_texts": True,
            "attributes": [],
            "compounding": []
        },
        {
            "tech_name": "0REGION",
            "object_type": "INFOOBJECT",
            "io_type": "CHA",
            "description": "Region / State",
            "datatype": "CHAR",
            "length": 3,
            "has_attributes": False,
            "has_texts": True,
            "attributes": ["0COUNTRY"],
            "compounding": ["0COUNTRY"]
        },
        {
            "tech_name": "0MATERIAL",
            "object_type": "INFOOBJECT",
            "io_type": "CHA",
            "description": "Material Number",
            "datatype": "CHAR",
            "length": 18,
            "has_attributes": True,
            "has_texts": True,
            "attributes": ["0MATL_GROUP", "0MATL_TYPE"],
            "compounding": []
        },
        {
            "tech_name": "0MATL_GROUP",
            "object_type": "INFOOBJECT",
            "io_type": "CHA",
            "description": "Material Group",
            "datatype": "CHAR",
            "length": 9,
            "has_attributes": False,
            "has_texts": True,
            "attributes": [],
            "compounding": []
        },
        {
            "tech_name": "0AMOUNT",
            "object_type": "INFOOBJECT",
            "io_type": "KYF", # Key Figure
            "description": "Net Amount in Local Currency",
            "datatype": "CURR",
            "length": 17,
            "decimals": 2,
            "unit_object": "0CURRENCY"
        },
        {
            "tech_name": "0QUANTITY",
            "object_type": "INFOOBJECT",
            "io_type": "KYF",
            "description": "Sales Quantity",
            "datatype": "QUAN",
            "length": 13,
            "decimals": 3,
            "unit_object": "0UNIT"
        },
        {
            "tech_name": "0CALDAY",
            "object_type": "INFOOBJECT",
            "io_type": "CHA",
            "description": "Calendar Day",
            "datatype": "DATS",
            "length": 8,
            "has_attributes": False,
            "has_texts": False,
            "attributes": [],
            "compounding": []
        }
    ],
    "adsos": [
        {
            "tech_name": "ADSO_SALES_STG",
            "object_type": "ADSO",
            "adso_type": "STAGING",
            "description": "Sales Inbound Staging DSO",
            "keys": ["VBELN"],
            "fields": ["ERDAT", "KUNNR", "NETWR", "WAERK"]
        },
        {
            "tech_name": "ADSO_SALES_CUBE",
            "object_type": "ADSO",
            "adso_type": "STANDARD",
            "description": "Sales Cube ADSO",
            "keys": ["0CUSTOMER", "0CALDAY"],
            "fields": ["0MATERIAL", "0AMOUNT", "0QUANTITY"]
        }
    ],
    "composite_providers": [
        {
            "tech_name": "HCPR_SALES_ANALYSIS",
            "object_type": "COMPOSITE_PROVIDER",
            "description": "CompositeProvider for Sales Data Mart",
            "sources": ["ADSO_SALES_CUBE"],
            "associations": [
                {"field": "0CUSTOMER", "target_io": "0CUSTOMER"},
                {"field": "0MATERIAL", "target_io": "0MATERIAL"}
            ]
        }
    ],
    "queries": [
        {
            "tech_name": "QUERY_SALES_OVERVIEW",
            "object_type": "BEX_QUERY",
            "description": "Executive Sales Analysis Query",
            "infoprovider": "HCPR_SALES_ANALYSIS",
            "variables": [
                {"name": "VAR_CALDAY", "io": "0CALDAY", "type": "SINGLE_OPTIONAL"}
            ],
            "key_figures": [
                {"tech_name": "0AMOUNT", "label": "Sales Amount"},
                {"tech_name": "CKF_GROSS_MARGIN", "label": "Calculated Gross Margin", "formula": "0AMOUNT * 0.15"}
            ]
        }
    ],
    "transformations": [
        {
            "tran_id": "TR_DS_TO_STG",
            "object_type": "TRANSFORMATION",
            "source_obj": "DS_SALES_HEADER",
            "target_obj": "ADSO_SALES_STG",
            "rule_type": "DIRECT",
            "field_mappings": [
                {"source": "VBELN", "target": "VBELN", "rule": "DIRECT"},
                {"source": "ERDAT", "target": "ERDAT", "rule": "DIRECT"},
                {"source": "KUNNR", "target": "KUNNR", "rule": "DIRECT"},
                {"source": "NETWR", "target": "NETWR", "rule": "DIRECT"},
                {"source": "WAERK", "target": "WAERK", "rule": "DIRECT"}
            ],
            "routines_abap": []
        },
        {
            "tran_id": "TR_STG_TO_CUBE",
            "object_type": "TRANSFORMATION",
            "source_obj": "ADSO_SALES_STG",
            "target_obj": "ADSO_SALES_CUBE",
            "rule_type": "ROUTINE",
            "field_mappings": [
                {"source": "KUNNR", "target": "0CUSTOMER", "rule": "DIRECT"},
                {"source": "ERDAT", "target": "0CALDAY", "rule": "DIRECT"},
                {"source": "NETWR", "target": "0AMOUNT", "rule": "FORMULA", "formula_expr": "IF(NETWR > 0, NETWR, 0)"}
            ],
            "routines_abap": [
                {
                    "routine_type": "START_ROUTINE",
                    "name": "FILTER_INVALID_CUSTOMERS",
                    "abap_code": "DATA: ls_source TYPE _ty_s_SC_1.\nDELETE SOURCE_PACKAGE WHERE KUNNR IS INITIAL OR KUNNR = '0000000000'."
                },
                {
                    "routine_type": "FIELD_ROUTINE",
                    "target_field": "0AMOUNT",
                    "abap_code": "RESULT = SOURCE_FIELDS-NETWR * 1.18. \" Apply 18% Tax Rate"
                }
            ]
        }
    ],
    "process_chains": [
        {
            "tech_name": "PC_DAILY_SALES_LOAD",
            "object_type": "PROCESS_CHAIN",
            "description": "Daily Sales Data Load Chain",
            "steps": [
                {"step_id": 1, "task_type": "DTP", "task_name": "DTP_DS_TO_STG"},
                {"step_id": 2, "task_type": "DTP", "task_name": "DTP_STG_TO_CUBE"},
                {"step_id": 3, "task_type": "INDEX_CREATE", "task_name": "ADSO_SALES_CUBE"}
            ]
        }
    ]
}
