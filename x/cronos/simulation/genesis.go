package simulation

import (
	"encoding/json"
	"fmt"
	"math/rand"

	"github.com/cosmos/cosmos-sdk/types/module"

	"github.com/crypto-org-chain/cronos/x/cronos/types"
)

const (
	ibcCroDenomKey          = "ibc_cro_denom"
	ibcTimeoutKey           = "ibc_timeout"
	cronosAdminKey          = "cronos_admin"
	enableAutoDeploymentKey = "enable_auto_deployment"
)

func GenIbcCroDenom(r *rand.Rand) string {
	// randDenom := make([]byte, 32)
	// r.Read(randDenom)
	// return fmt.Sprintf("ibc/%s", hex.EncodeToString(randDenom))
	return types.IbcCroDenomDefaultValue
}

func GenIbcTimeout(r *rand.Rand) uint64 {
	// timeout := r.Uint64()
	// return timeout
	return 712146093122746616
}

func GenCronosAdmin(r *rand.Rand, simState *module.SimulationState) string {
	// adminAccount, _ := simtypes.RandomAcc(r, simState.Accounts)
	// return adminAccount.Address.String()
	return "cosmos1whw0gmdh82ctlkwjqrnwgqsz59qvffvxv6lu5h"
}

func GenEnableAutoDeployment(r *rand.Rand) bool {
	enableAutoDeployment := r.Intn(2) > 0
	return enableAutoDeployment
}

// RandomizedGenState generates a random GenesisState for the cronos module
func RandomizedGenState(simState *module.SimulationState) {
	// cronos params
	var (
		ibcCroDenom          string
		ibcTimeout           uint64
		cronosAdmin          string
		enableAutoDeployment bool
	)

	ibcCroDenom = types.IbcCroDenomDefaultValue
	ibcTimeout = 712146093122746616
	cronosAdmin = "cosmos1whw0gmdh82ctlkwjqrnwgqsz59qvffvxv6lu5h"
	// if we use rand here it will cause non determinism, but if we comment this line everything is fine.
	_ = simState.Rand.Intn(100)
	enableAutoDeployment = false
	fmt.Printf("enableAutoDeploment value: %v\n", enableAutoDeployment)

	params := types.NewParams(ibcCroDenom, ibcTimeout, cronosAdmin, enableAutoDeployment)
	cronosGenesis := &types.GenesisState{
		Params:            params,
		ExternalContracts: nil,
		AutoContracts:     nil,
	}

	bz, err := json.MarshalIndent(cronosGenesis, "", " ")
	if err != nil {
		panic(err)
	}
	fmt.Printf("Selected randomly generated %s parameters:\n%s\n", types.ModuleName, bz)

	simState.GenState[types.ModuleName] = simState.Cdc.MustMarshalJSON(cronosGenesis)
	// simState.GenState[types.ModuleName] = simState.Cdc.MustMarshalJSON(types.DefaultGenesis())
}
