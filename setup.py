from distutils.core import setup

setup(
  name="SchemaCompare",
  version="1.0.0",
  author="Simo-Pekka Kerkelä",
  author_email="simopekka1990@gmail.com",
  url="TODO",
  description="Utility to see schema changes over time",
  scripts=['schemacompare'],
  packages=["package"],
  install_requires=[
    "psycopg2",
    "deepdiff"
  ]
)