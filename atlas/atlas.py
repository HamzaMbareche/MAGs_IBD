import os, sys
from .color_logger import logger

import multiprocessing

import subprocess
import click


from snakemake.io import load_configfile
from .make_config import make_config, validate_config
from .init.atlas_init import run_init, run_init_sra

from .__init__ import __version__

##


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__)
@click.pass_context
def cli(obj):
    """ATLAS - workflows for assembly, annotation, and genomic binning of
    metagenomic and metatranscriptomic data.

    For updates and reporting issues, see: https://github.com/metagenome-atlas/atlas
    """


cli.add_command(run_init)


cli.add_command(run_init_sra)


def get_snakefile(file="workflow/Snakefile"):
    sf = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    if not os.path.exists(sf):
        sys.exit("Unable to locate the Snakemake workflow file; tried %s" % sf)
    return sf


## QC command


@cli.command(
    "run",
    context_settings=dict(ignore_unknown_options=True),
    short_help="run atlas main workflow",
)
@click.argument(
    "workflow",
    type=click.Choice(
        ["qc", "assembly", "binning", "genomes", "genecatalog", "None", "all"]
    ),
    #    show_default=True,
    #    help="Execute only subworkflow.",
)
@click.option(
    "-w",
    "--working-dir",
    type=click.Path(dir_okay=True, writable=True, resolve_path=True),
    help="location to run atlas.",
    default=".",
)
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True, resolve_path=True),
    help="config-file generated with 'atlas init'",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=multiprocessing.cpu_count(),
    help="use at most this many jobs in parallel (see cluster submission for mor details).",
)
@click.option(
    "--profile",
    default=None,
    help="snakemake profile e.g. for cluster execution.",
)
@click.option(
    "-n",
    "--dryrun",
    is_flag=True,
    default=False,
    show_default=True,
    help="Test execution.",
)
@click.argument("snakemake_args", nargs=-1, type=click.UNPROCESSED)
def run_workflow(
    workflow, working_dir, config_file, jobs, profile, dryrun, snakemake_args
):
    """Runs the ATLAS pipline

    By default all steps are executed but a sub-workflow can be specified.
    Needs a config-file and expects to find a sample table in the working-directory. Both can be generated with 'atlas init'

    Most snakemake arguments can be appended to the command for more info see 'snakemake --help'

    For more details, see: https://metagenome-atlas.readthedocs.io
    """

    logger.info(f"Atlas version: {__version__}")

    if config_file is None:
        config_file = os.path.join(working_dir, "config.yaml")

    if not os.path.exists(config_file):
        logger.critical(
            f"config-file not found: {config_file}\n" "generate one with 'atlas init'"
        )
        exit(1)

    sample_file = os.path.join(working_dir, "samples.tsv")

    if not os.path.exists(sample_file):
        logger.critical(
            f"sample.tsv not found in the working directory. "
            "Generate one with 'atlas init'"
        )
        exit(1)

    validate_config(config_file, workflow)

    conf = load_configfile(config_file)

    db_dir = conf["database_dir"]

    cmd = (
        "snakemake --snakefile {snakefile} --directory {working_dir} "
        "{jobs} --rerun-incomplete "
        "--configfile '{config_file}' --nolock "
        " {profile} --use-conda {conda_prefix} {dryrun} "
        " --scheduler greedy "
        " {target_rule} "
        " {args} "
    ).format(
        snakefile=get_snakefile(),
        working_dir=working_dir,
        jobs="--jobs {}".format(jobs) if jobs is not None else "",
        config_file=config_file,
        profile="" if (profile is None) else "--profile {}".format(profile),
        dryrun="--dryrun" if dryrun else "",
        args=" ".join(snakemake_args),
        target_rule=workflow if workflow != "None" else "",
        conda_prefix="--conda-prefix " + os.path.join(db_dir, "conda_envs"),
    )
    logger.debug("Executing: %s" % cmd)
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        # removes the traceback
        logger.critical(e)
        exit(1)


# Download
@cli.command(
    "download",
    context_settings=dict(ignore_unknown_options=True),
    short_help="download reference files (need ~50GB)",
)
@click.option(
    "-d",
    "--db-dir",
    help="location to store databases",
    type=click.Path(dir_okay=True, writable=True, resolve_path=True),
    required=True,
)
@click.option(
    "-j",
    "--jobs",
    default=1,
    type=int,
    show_default=True,
    help="number of simultaneous downloads",
)
@click.argument("snakemake_args", nargs=-1, type=click.UNPROCESSED)
def run_download(db_dir, jobs, snakemake_args):
    """Executes a snakemake workflow to download reference database files and validate based on
    their MD5 checksum.
    """

    cmd = (
        "snakemake --snakefile {snakefile} "
        "--jobs {jobs} --rerun-incomplete "
        "--conda-frontend mamba --scheduler greedy "
        "--nolock  --use-conda  --conda-prefix {conda_prefix} "
        "--config database_dir='{db_dir}' {add_args} "
        "{args}"
    ).format(
        snakefile=get_snakefile("workflow/rules/download.smk"),
        jobs=jobs,
        db_dir=db_dir,
        conda_prefix=os.path.join(db_dir, "conda_envs"),
        add_args="" if snakemake_args and snakemake_args[0].startswith("-") else "--",
        args=" ".join(snakemake_args),
    )
    logger.debug("Executing: " + cmd)
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        # removes the traceback
        logger.critical(e)
        exit(1)


if __name__ == "__main__":
    cli()
