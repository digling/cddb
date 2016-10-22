# CDDB: Chinese Dialect Database

This database aggregates all kinds of linguistic information on Chinese dialects, ranging from lexical datasets, via lists of character readings in ancient and contemporary varieties, up to proposed classifications. The database is handled with help of a Python library that tests whether the data is correctly encoded and handles its consistency. The Python library itself has some dependencies which are currently being developed, including the [concepticon api](http://github.com/clld/concepticon-data), parts of the [lexibank-api](http://github.com/glottobank/lexibank-data), the [cross-linguistic phonetic alphabet](http://github.com/glottobank/clpa), [lingpy](http://lingpy.org), and the currently not yet released [CLICS api](http://github.com/clics/clics-data) for network manipulations as well as [sinopy](http://github.com/lingpy/sinopy). To edit the data, the [edictor tool](http://digling/edictor) will be used.

## Data Types in CDDB

Currently, I envision to include the following datatypes (for which exemplary datasets already exist):

* lexemes (word lists) in different dialects
* character readings (character lists) in different dialects and language varieties, including older stages of the language
* corpora on character readings (examples include fǎnqiè readings, rhyme annotations, etc.)
* structural data on dialects ("structural" is here understood in wide sense, I mostly think of datasets in which a set of features is attributed in an abstract manner, e.g., by listing presence and absence, to a set of dialect varieties)
* similarity data on dialects (I think of tables on mutual intelligibility, as they are listed in some studies)
* classification data (I think of explicit trees, but potentially also simple grouping information)

## How Data will be Added

Data will be added in an ad-hoc manner: If I realized that certain data is available, I'll start trying to figure out how to add it, be it by typing it off myself (see dataset Liu2007), or by looking for sources where it was published in a digitally accessible manner. The new source will be added to the references, and a folder containing the data will be created in the folder datasets/ in the repository. But the appearance of the data may change, as errors will be corrected and at times new aspects will be added (enhanced cognate judgments, etc.). Since the data will be in flux to some degree, releases will help to fix certain stages of the data, and make sure users can employ one version that is physically stored and given a DOI at [zenodo](http://zenodo.org).

