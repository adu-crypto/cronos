from pathlib import Path
import json

import pytest
from web3 import Web3

from .network import setup_custom_cronos
from dateutil.parser import isoparse
from .utils import (
    ADDRS,
    CONTRACTS,
    KEYS,
    deploy_contract,
    send_txs,
    sign_transaction,
    wait_for_new_blocks,
    wait_for_block_time,
    parse_events,
)


@pytest.fixture(scope="module")
def cronos_gov(tmp_path_factory):
    path = tmp_path_factory.mktemp("cronos-gov")
    yield from setup_custom_cronos(
        path, 26300, Path(__file__).parent / "configs/default.jsonnet"
    )


def test_gov_update_params(cronos_gov, tmp_path):
    cli = cronos_gov.cosmos_cli()

    proposal = tmp_path / "proposal.json"
    # governance module account as signer
    signer = "crc10d07y265gmmuvt4z0w9aw880jnsr700jdufnyd"
    proposal_src = {
        "messages": [
            {
                "@type": "/cronos.MsgUpdateParams",
                "authority": signer,
                "params": {
                    "cronos_admin": "crc12luku6uxehhak02py4rcz65zu0swh7wjsrw0pp",
                    "enable_auto_deployment": False,
                    "ibc_cro_denom": "ibc/6411AE2ADA1E73DB59DB151"
                    "A8988F9B7D5E7E233D8414DB6817F8F1A01600000",
                    "ibc_timeout": "96400000000000", 
                }
            }
        ],
        "deposit": "1basetcro",
    }
    proposal.write_text(json.dumps(proposal_src))
    rsp = cli.submit_gov_proposal(proposal, from_="community")

    assert rsp["code"] == 0, rsp["raw_log"]

    # get proposal_id
    ev = parse_events(rsp["logs"])["submit_proposal"]
    proposal_id = ev["proposal_id"]
    print("gov proposal submitted", proposal_id)

    # not sure why, but sometimes can't find the proposal immediatelly
    wait_for_new_blocks(cli, 1)
    proposal = cli.query_proposal(proposal_id)

    # each validator vote yes
    for i in range(len(cronos_gov.config["validators"])):
        rsp = cronos_gov.cosmos_cli(i).gov_vote("validator", proposal_id, "yes")
        assert rsp["code"] == 0, rsp["raw_log"]
    wait_for_new_blocks(cli, 1)
    assert (
        int(cli.query_tally(proposal_id)["yes_count"]) == cli.staking_pool()
    ), "all validators should have voted yes"
    print("wait for proposal to be activated")
    wait_for_block_time(cli, isoparse(proposal["voting_end_time"]))
    wait_for_new_blocks(cli, 1)

    print("check params have been updated now")
    rsp = cli.query_params()
    print("params", rsp)
    assert rsp == {
        "cronos_admin": "crc12luku6uxehhak02py4rcz65zu0swh7wjsrw0pp",
        "enable_auto_deployment": False,
        "ibc_cro_denom": "ibc/6411AE2ADA1E73DB59DB151"
        "A8988F9B7D5E7E233D8414DB6817F8F1A01600000",
        "ibc_timeout": "96400000000000",
    }
