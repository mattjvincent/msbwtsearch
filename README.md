docker network create --attachable proj1_test

docker run --rm -p 8000:8000 --name SOMENAME --network qtlviewertest -v /Users/mvincent/work/qtlviewer/data/Attie_DO378_eQTL_viewer_v3.RData:/app/qtlapi/data/ppppppppppppppdata.RData -v /Users/mvincent/work/qtlviewer/data/ccfoundersnps.sqlite:/app/qtlapi/data/ccfounders.sqlite -v /Users/mvincent/work/qtlviewer/qtlapi/qtlapi.R:/app/qtlapi/qtlapi.R mattjvincent/qtlapi /app/qtlapi/qtlapi.R

Than in docker-compose.yml...

networks:
  default:
    external:
      name: qtlviewertest



# QTL Viewer
===================

This is a web application that renders QTL "type" data.  There are multiple components and moving parts, but 2 different main projects ake up the QTL Viewer.

## QTL API

The QTL API utilizes the following technology stack:

* [Docker](http://www.docker.com/) - Build, Ship, and Run Any App, Anywhere 
* [R](http://www.r-project.org/) - number cruncher
* [R/qtl2](http://kbroman.org/qtl2/) - Analysis 
* [Plumber](http://www.rplumber.io/) - Help turn R code into Web based API


The API generated is used by the QTL Web app.  The following API's are supplied:

#### /datasets

Description: The initial API called by QTL Web.  The data returned is dependent upon if the "dataType" is "mRNA", "protein", or "phenotype". The purpose of this API is to define and describe the datasets used in the viewer.

Parameters: None

Example response:
```
{"dataSets": [{
    "id": "some.dataset.identifier",
    "displayName": "Some Dataset",
    "dataType": "mRNA",
    "gene_ids": [
         "ENSMUSG00000000001",
         "ENSMUSG00000000028",
         "ENSMUSG00010203821",
         ...
    ],
    "protein_ids": [],
    "phenotypes" : [],
    "covarFactors":[{
        "column.name":"sex",
        "display.name":"Sex"
    }, {
        "column.name":"gen",
        "display.name":"Generation"}]
    },
    ...
    ],
    "ensemblVersion": 75,
    "numMarkers": 68433    
}
```

#### /lodscan

Description: Perform a LOD Scan.

Parameters:

| Parameter | Description |
| ------ | ------ |
| dataset | dataset identifier |
| id | the identifer to perform LOD scan on |
| regressLocal | TRUE to regress on local genotype, FALSE to not |
| nCores | number of cores to use |
| expand | TRUE to expand the JSON, FALSE to condense |

Example response (expanded):

```
{"result": [
    {"id":"1_4530778","chr":"1","pos":4.5308,"lod":1.688},
    {"id":"1_4533435","chr":"1","pos":4.5334,"lod":1.6709},
    ...
    {"id":"1_4536092","chr":"1","pos":4.5361,"lod":1.6539}
],
 "time":5.3
}
```

#### /foundercoefs

Description: Get founder coefficients.

Parameters:

| Parameter | Description |
| ------ | ------ |
| dataset | dataset identifier |
| id | the identifer to perform LOD scan on |
| chrom | the chromosome |
| regressLocal | TRUE to regress on local genotype, FALSE to not |
| blup | TRUE to perform Best Linear Unbiased Predictors  |
| center | TRUE to center around 0 |
| nCores | number of cores to use |
| expand | TRUE to expand the JSON, FALSE to condense |

Example response (expanded):

```
{"result":[{"id":"2_4292516","chr":"2","pos":4.2925,
            "A":0.012,"B":-0.0267,"C":0.0345,"D":0.1994,
            "E":0.1305,"F":-0.4769,"G":0.1217,"H":0.0055},
           {"id":"2_4337139","chr":"2","pos":4.3371,
            "A":0.0114,"B":-0.0267,"C":0.0343,"D":0.2,
            "E":0.1307,"F":-0.4769,"G":0.1218,"H":0.0055},
            ...
           {"id":"2_4369263","chr":"2","pos":4.3693,
            "A":0.012,"B":-0.0259,"C":0.0407,"D":0.2006,
            "E":0.1323,"F":-0.4783,"G":0.1134,"H":0.0052}
        ],
 "time":2.3
}
```

#### /expression

Description: Get the expression data.

Parameters:

| Parameter | Description |
| ------ | ------ |
| dataset | dataset identifier |
| id | the identifer to perform LOD scan on |

Example response:

```
{"data":[{"mouse_id":"F01","Sex":"F","Generation":"G4","Litter":2,
          "Diet":"hf","Coat.Color":"agouti","GenerationLitter":"G4_2",
          "expression":0.2243,"_row":"F01"},
          ...
         {"mouse_id":"F02","Sex":"F","Generation":"G4","Litter":2,
          "Diet":"hf","Coat.Color":"black","GenerationLitter":"G4_2",
          "expression":0.3498,"_row":"F02"}
         ],
 "time":2.3
}
```

#### /mediate

Description: Perform mediation analysis.

Parameters:

| Parameter | Description |
| ------ | ------ |
| dataset | dataset identifier |
| id | the identifer to perform LOD scan on |
| mid | marker identifier |
| expand | TRUE to expand the JSON, FALSE to condense |

Example response:

```
{"result":[{"gene_id":"ENSMUSG00000000001","symbol":"Gnai3",
            "chr":"3","pos":108.1267,"LOD":1.3625},
           {"gene_id":"ENSMUSG00000000028","symbol":"Cdc45",
            "chr":"16","pos":18.7962,"LOD":1.605},
           ...
           {"gene_id":"ENSMUSG00000000037","symbol":"Scml2",
            "chr":"X","pos":161.1877,"LOD":1.2535}
     ],
 "time":10.3
}
```

#### /snpassoc

Description: SNP Association Mappting

Parameters:

| Parameter | Description |
| ------ | ------ |
| dataset | dataset identifier |
| id | the identifer to perform LOD scan on |
| chrom | the chromosome |
| location | chromosomal location |
| windowSize | the window size, distance on each size of location |
| nCores | number of cores to use |
| expand | TRUE to expand the JSON, FALSE to condense |

Example response:

```
{"result":[{"snp":"rs245710663","chr":"1","pos":14.5001,
            "alleles":"G|C","sdp":64,"ensembl_gene":"",
            "csq":"intergenic_variant","index":1,"interval":147,
            "on_map":false,"lod":0.0015},
           {"snp":"rs263649601","chr":"1","pos":14.5002,
            "alleles":"C|T","sdp":64,"ensembl_gene":"",
            "csq":"intergenic_variant","index":1,"interval":147,
            "on_map":false,"lod":0.0015},
           ...
           {"snp":"rs32279922","chr":"1","pos":14.5004,
            "alleles":"C|T","sdp":153,"ensembl_gene":"",
            "csq":"intergenic_variant","index":3,"interval":147,
            "on_map":false,"lod":3.5395e-06}
         ],
 "time":11.1
}
```



## QTL Web

* [Docker](http://www.docker.com/) - Build, Ship, and Run Any App, Anywhere 
* [Python](http://www.python.org/) - Web framework
* [Celery](http://www.celeryproject.org/) - Distributed Task Queue
* [Redis](http://redis.io/) - Message Broker
* [Bootstrap 4](http://getbootstrap.com/) - HTML enhanced for web apps!



QTL Viewer uses a number of other projects to work properly:

* [Docker](http://www.docker.com/) - Build, Ship, and Run Any App, Anywhere 
* [Bootstrap 4](http://https://getbootstrap.com/) - HTML enhanced for web apps!
* [R](https://www.r-project.org/) - number cruncher
* [markdown-it] - Markdown parser done right. Fast and easy to extend.
* [Twitter Bootstrap] - great UI boilerplate for modern web apps
* [node.js] - evented I/O for the backend
* [Express] - fast node.js network app framework [@tjholowaychuk]
* [Gulp] - the streaming build system
* [Breakdance](http://breakdance.io) - HTML to Markdown converter
* [jQuery] - duh


