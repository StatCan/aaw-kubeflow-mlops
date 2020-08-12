import argparse
import pandas as pd
from sodapy import Socrata


DEFAULT_LIMIT = 100000

# Columns pulled from API
# Item description (name), vendor name, category name
COLUMNS = ['im_desc', 'vendor_name', 'category_name']
COLUMN_RENAME_MAP = {
    'im_desc': 'item_name'
}

def parse_args():
    parser = argparse.ArgumentParser(description="Gets Iowa Liquor Sales data from API and stores to a minio destination")
    parser.add_argument(
        'output_file',
        action='store',
        help="Name of the local file to store data to.  Must be .csv"
    )
    parser.add_argument(
        '--limit',
        action='store',
        default=DEFAULT_LIMIT,
        help=f'Maximum number of records requested per month (default: {DEFAULT_LIMIT}'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Technically kinda a secret, but anyone can get it by clicking a form...
    socrata_access_key = "SUVTrMEtyXaYiak2kxBOy54JU"

    source_client = Socrata("data.iowa.gov",
                            socrata_access_key
                            )

    select = ", ".join(COLUMNS)
    limit = int(args.limit)
    order = "date"
    source_key = "m3tr-qhgy"
    # TODO: Make this distinct so I don't get repeat items and have less problem with dedup later
    where = f"date >= '2017-01' AND date < '2018-01'"
    results = source_client.get(source_key,
                                select=select,
                                order="date",
                                where=where,
                                limit=limit,
                                )
    df = pd.DataFrame(results)
    
    # Order of returned columns is not guaranteed.  Reorder them to be how we originally specified
    df = df[COLUMNS]
    
    # Apply useful names
    df = df.rename(columns=COLUMN_RENAME_MAP)
    
    df.to_csv(args.output_file, index=False)
    
    df.to_csv(
    )
    
#     # Save to csv
#     if not args.no_csv:
#         this_data_cfg = data_cfg[args.data_spec]["csv"]
#         with Timer(enter_message=f"Uploading csv data", exit_message="--> upload csv complete"):
#             output_url = url_template.format(
#                 bucket=this_data_cfg["bucket"],
#                 key_base=this_data_cfg["key_base"],
#                 suffix=this_data_cfg["suffix"]
#             )

#             # Could partition this data further (daily files)
#             wr.s3.to_csv(
#                 df=df,
#                 path=output_url,
#                 s3_additional_kwargs=s3_additional_kwargs,
#                 index=False,  # Do not export empty index column
#             )

#     # Save to parquet
#     if not args.no_pq:
#         this_data_cfg = data_cfg[args.data_spec]["parquet"]
#         with Timer(enter_message=f"Uploading parquet data", exit_message="--> upload csv complete"):
#             output_url = url_template.format(
#                 bucket=this_data_cfg["bucket"],
#                 key_base=this_data_cfg["key_base"],
#                 suffix=this_data_cfg["suffix"]
#             )

#             # Could partition this data further (daily files)
#             wr.s3.to_parquet(
#                 df=df,
#                 path=output_url,
#                 s3_additional_kwargs=s3_additional_kwargs,
#                 # compression=this_data_cfd["compression"],  # psycopg2 does not support copy redshift from
#                 # compressed parquet
#                 index=False,  # Do not export empty index column
#             )
