#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import os

import experiment.service.db


def getenv(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    logging.getLogger().setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(
        description="Launch the ST4SD LAMMPS package for a fresh run followed by restart iterations using PVC inputs."
    )
    parser.add_argument(
        "--pvep",
        default=os.environ.get("ST4SD_PVEP_NAME", "st4sd-lammps-with-restart"),
        help="Registered PVEP name (default: %(default)s)",
    )
    parser.add_argument(
        "--pvc",
        default=os.environ.get("ST4SD_INPUT_PVC", "md-simulation-inputs-pvc-rwx"),
        help="PVC containing npt.in and confin.data (default: %(default)s)",
    )
    parser.add_argument(
        "--volume-identifier",
        default=os.environ.get("ST4SD_VOLUME_IDENTIFIER", "myVolume"),
        help="Identifier of the mounted PVC volume in the payload (default: %(default)s)",
    )
    parser.add_argument(
        "--source-file",
        default=os.environ.get("ST4SD_SOURCE_FILE", "lammps_with_restart_data/npt.in"),
        help="Path to npt.in relative to the root of the PVC (default: %(default)s)",
    )
    parser.add_argument(
        "--target-file",
        default=os.environ.get("ST4SD_TARGET_FILE", "file.in"),
        help="Target input filename for the experiment (default: %(default)s)",
    )
    parser.add_argument(
        "--confin-source",
        default=os.environ.get("ST4SD_CONFIN_SOURCE", "lammps_with_restart_data/confin.data"),
        help="Path to confin.data relative to the root of the PVC (default: %(default)s)",
    )
    parser.add_argument(
        "--confin-target",
        default=os.environ.get("ST4SD_CONFIN_TARGET", "confin.data"),
        help="Target confin.data filename for the experiment (default: %(default)s)",
    )
    parser.add_argument(
        "--restart-config-source",
        default=os.environ.get("ST4SD_RESTART_CONFIG_SOURCE", "lammps_with_restart_data/restart_iterations.txt"),
        help="Path to the restart-iteration config file relative to the root of the PVC (default: %(default)s)",
    )
    parser.add_argument(
        "--restart-config-target",
        default=os.environ.get("ST4SD_RESTART_CONFIG_TARGET", "restart-config"),
        help="Target restart iteration config filename for the experiment (default: %(default)s)",
    )
    args = parser.parse_args()

    api = experiment.service.db.ExperimentRestAPI(
        getenv("ST4SD_RUNTIME_URL"),
        cc_auth_token=getenv("ST4SD_TOKEN"),
    )

    payload = {
        "inputs": [
            {
                "sourceFilename": args.source_file,
                "targetFilename": args.target_file,
                "volume": args.volume_identifier,
            },
            {
                "sourceFilename": args.confin_source,
                "targetFilename": args.confin_target,
                "volume": args.volume_identifier,
            },
            {
                "sourceFilename": args.restart_config_source,
                "targetFilename": args.restart_config_target,
                "volume": args.volume_identifier,
            },
        ],
        "volumes": [
            {
                "identifier": args.volume_identifier,
                "type": {
                    "persistentVolumeClaim": args.pvc,
                },
            },
        ],
    }

    uid = api.api_experiment_start(args.pvep, payload)
    print(uid)


if __name__ == "__main__":
    main()
