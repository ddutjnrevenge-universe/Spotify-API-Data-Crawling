import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame

# Script generated for node Remove symbols artists
def MyTransform(glueContext, dfc) -> DynamicFrame:
    from pyspark.sql.functions import regexp_replace, col, udf, to_date
    from pyspark.sql.types import StringType
    from sklearn.preprocessing import LabelEncoder, MinMaxScaler
    import ast
    import pandas as pd
    import numpy as np
    from pyspark.sql import SparkSession

    # Convert the input DynamicFrame to a DataFrame
    df = dfc.select(list(dfc.keys())[0]).toDF()

    # Perform the transformation to remove symbols from the 'artists' column
    df = df.withColumn('artists', regexp_replace('artists', r"[\[\]']", ''))

    # UDF to extract first genre or return 'unknown'
    def extract_first_genre(genre_list):
        genre_list = ast.literal_eval(genre_list)
        return genre_list[0] if genre_list else "unknown"

    extract_genre_udf = udf(extract_first_genre, StringType())

    # Apply the UDF to the 'artist_genres' column
    df = df.withColumn('artist_genres', extract_genre_udf(col('artist_genres')))

    # Drop duplicates
    df = df.dropDuplicates()

    # Convert 'explicit' column to integer
    df = df.withColumn('explicit', col('explicit').cast('int'))

    # Convert 'release_date' to datetime
    df = df.withColumn('release_date', to_date(col('release_date')))

    # Apply Label Encoding on 'artist_genres'
    spark = SparkSession.builder.getOrCreate()
    pandas_df = df.toPandas()
    label_encoder = LabelEncoder()
    pandas_df['artist_genres_encoded'] = label_encoder.fit_transform(pandas_df['artist_genres'])

    # Select numeric features
    features = pandas_df.select_dtypes(np.number).columns

    # Apply MinMaxScaler
    scaler = MinMaxScaler()
    pandas_df[features] = scaler.fit_transform(pandas_df[features])

    # Convert the pandas DataFrame back to Spark DataFrame
    df = spark.createDataFrame(pandas_df)

    # Convert the transformed DataFrame back to a DynamicFrame
    transformed_dynamic_frame = DynamicFrame.fromDF(df, glueContext, "transformed_dynamic_frame")

    return transformed_dynamic_frame

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Data
Data_node1724212075306 = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False},
    connection_type="s3",
    format="csv",
    connection_options={"paths": ["s3://batch10-nguyentnh-proj-athena/Unsaved/2024/08/16/5db03a81-6082-47c1-9e80-678e6e95fcdc.csv"], "recurse": True},
    transformation_ctx="Data_node1724212075306"
)

# Script generated for node Select relevant features
Selectrelevantfeatures_node1724216209451 = SelectFields.apply(
    frame=Data_node1724212075306,
    paths=["followers", "instrumentalness", "danceability", "explicit", "key", "artist_genres", "artists", "track_name", "release_date", "duration_sec", "track_popularity", "album_name", "album_popularity", "label", "liveness", "tempo", "acousticness", "speechiness", "mode", "loudness", "energy", "valence", "time_signature"],
    transformation_ctx="Selectrelevantfeatures_node1724216209451"
)

# Script generated for node Change Schema
ChangeSchema_node1724218707491 = ApplyMapping.apply(
    frame=Selectrelevantfeatures_node1724216209451,
    mappings=[
        ("followers", "string", "followers", "int"),
        ("instrumentalness", "string", "instrumentalness", "float"),
        ("danceability", "string", "danceability", "float"),
        ("explicit", "string", "explicit", "boolean"),
        ("key", "string", "key", "int"),
        ("artist_genres", "string", "artist_genres", "string"),
        ("artists", "string", "artists", "string"),
        ("track_name", "string", "track_name", "string"),
        ("release_date", "string", "release_date", "date"),
        ("duration_sec", "string", "duration_sec", "float"),
        ("track_popularity", "string", "track_popularity", "int"),
        ("album_name", "string", "album_name", "string"),
        ("album_popularity", "string", "album_popularity", "int"),
        ("label", "string", "label", "string"),
        ("liveness", "string", "liveness", "float"),
        ("tempo", "string", "tempo", "float"),
        ("acousticness", "string", "acousticness", "float"),
        ("speechiness", "string", "speechiness", "float"),
        ("mode", "string", "mode", "int"),
        ("loudness", "string", "loudness", "float"),
        ("energy", "string", "energy", "float"),
        ("valence", "string", "valence", "float"),
        ("time_signature", "string", "time_signature", "int")
    ],
    transformation_ctx="ChangeSchema_node1724218707491"
)

# Script generated for node Remove symbols artists
Removesymbolsartists_node1724216822845 = MyTransform(
    glueContext,
    DynamicFrameCollection({"ChangeSchema_node1724218707491": ChangeSchema_node1724218707491}, glueContext)
)

# Script generated for node S3 Sink
glueContext.write_dynamic_frame.from_options(
    frame=Removesymbolsartists_node1724216822845,
    connection_type="s3",
    connection_options={"path": "s3://batch10-nguyentnh-proj/processed/"},
    format="parquet",
    transformation_ctx="S3Sink"
)

job.commit()
