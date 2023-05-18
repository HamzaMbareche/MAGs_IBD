# MAGs_IBD

[![Anaconda-Server Badge](https://anaconda.org/bioconda/metagenome-atlas/badges/latest_release_relative_date.svg)](https://anaconda.org/bioconda/metagenome-atlas)
[![Bioconda](https://img.shields.io/conda/dn/bioconda/metagenome-atlas.svg?label=Bioconda )](https://anaconda.org/bioconda/metagenome-atlas)
[![Documentation Status](https://readthedocs.org/projects/metagenome-atlas/badge/?version=latest)](https://metagenome-atlas.readthedocs.io/en/latest/?badge=latest)
[![follow on twitter](https://img.shields.io/twitter/follow/SilasKieser.svg?style=social&label=Follow)](https://twitter.com/search?f=tweets&q=%40SilasKieser%20%23metagenomeAtlas&src=typd)


MAGs_IBD is a easy-to-use metagenomic pipeline based on snakemake. It handles all steps from QC, Assembly, Binning, to Annotation.

![scheme of workflow]

You can start using atlas with three commands:
```
    mamba install -y -c bioconda -c conda-forge metagenome-atlas={latest_version}
    atlas init --db-dir databases path/to/fastq/files
    atlas run all
```
where `{latest_version}` should be replaced by [![Version](https://anaconda.org/bioconda/metagenome-atlas/badges/version.svg)](https://anaconda.org/bioconda/metagenome-atlas)


# Developpment/Extensions

Here are some ideas I work or want to work on when I have time. If you want to contribute or have some ideas let me know via a feature request issue.

- Optimized MAG recovery (e.g. [Spacegraphcats](https://github.com/spacegraphcats/spacegraphcats))
- Integration of viruses/plasmid that live for now as [extensions](https://github.com/metagenome-atlas/virome_atlas)
- Add statistics and visualisations as in [atlas_analyze](https://github.com/metagenome-atlas/atlas_analyze)
- Implementation of most rules as snakemake wrapper
- Cloud execution
- Update to new Snakemake version and use cool reports.
