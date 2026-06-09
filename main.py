from environment import Environment
from decision_makers import (
    Agent,
    AllHorizontal,
    AllLocal,
    AllVertical,
    BalancedCyclicOffloader,
    MinimumLatencyEstimationOffloader,
    Random,
    SingleAgent,
    RoundRobin,
    RuleBased,
)
from decision_makers.baselines import official_policy_map
from lr_schedulers import constant,Linear
from phase1_tracing import TraceRecorder
from phase2_mechanisms import build_policy_map
from delayed_reward_runtime import process_delayed_reward_events
import numpy as np
import argparse
import torch
import os
import json
import pickle 
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    if yaml is not None:
        with config_path.open() as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError("config.yml must contain a mapping")
        return data
    data: dict[str, object] = {}
    for raw_line in config_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError("config.yml must use key: value entries")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _coerce_args_from_config(parser, args, config):
    for key, value in config.items():
        if not hasattr(args, key):
            continue
        current = getattr(args, key)
        if current != parser.get_default(key):
            continue
        setattr(args, key, value)
    return args


def _maybe_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _maybe_bool(value, default):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower().strip()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return default


def select_torch_device() -> str:
    return "cpu"


def main():
    device = select_torch_device()
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.yml', help='Path to run configuration file')
    parser.add_argument('--log_folder', type=str, default='log_folder', help='Path to the log folder')
    parser.add_argument('--hyperparameters_file', type=str, default='hyperparameters/hyperparameters.json', help='Path to the hyperparameters file')
    parser.add_argument('--epochs', type=int, default=2, help='Device to use')
    parser.add_argument('--validate', type=bool, default=False, help='Device to use')
    parser.add_argument('--trace_output_dir', type=str, default='outputs/phase1_traces', help='Path to trace output directory')
    parser.add_argument('--seed', type=int, default=None, help='Optional random seed for reproducible validation runs')
    parser.add_argument('--trace_level', type=str, default='full', choices=('full', 'summary'), help='Trace emission level')
    args  = parser.parse_args()

    config = _load_config(args.config)
    if config:
        args = _coerce_args_from_config(parser, args, config)
        if "epochs" in config:
            args.epochs = _maybe_int(config["epochs"], args.epochs)
        if "validate" in config:
            args.validate = _maybe_bool(config["validate"], args.validate)
        if "log_folder" in config:
            args.log_folder = str(config["log_folder"])
        if "hyperparameters_file" in config:
            args.hyperparameters_file = str(config["hyperparameters_file"])
        if "trace_output_dir" in config:
            args.trace_output_dir = str(config["trace_output_dir"])
        if "trace_level" in config:
            args.trace_level = str(config["trace_level"])
        if "seed" in config and args.seed is None:
            args.seed = _maybe_int(config["seed"], args.seed)
        step_log_interval = _maybe_int(config.get("step_log_interval", 10), 10)
        episode_log_interval = _maybe_int(config.get("episode_log_interval", 10), 10)
    else:
        step_log_interval = 10
        episode_log_interval = 10

    if args.seed is not None:
        np.random.seed(int(args.seed))
        torch.manual_seed(int(args.seed))
        # Static-frequency task injection still occurs inside Environment.reset(),
        # but seeding here makes the surrounding validation run reproducible.

    os.makedirs(args.log_folder, exist_ok=True)
    trace_recorder = TraceRecorder(trace_level=args.trace_level)
    with open(args.hyperparameters_file) as f:
        hyperparameters = json.load(f)
            
    number_of_servers=  hyperparameters['number_of_servers']
    env = Environment(
        number_of_servers=hyperparameters['number_of_servers'],
        private_cpu_capacities=hyperparameters['private_cpu_capacities'],
        public_cpu_capacities=hyperparameters['public_cpu_capacities'],
        connection_matrix=hyperparameters['connection_matrix'],
        cloud_computational_capacity=hyperparameters['cloud_computational_capacity'],
        episode_time=hyperparameters['episode_time'],
        static_frequency=hyperparameters['static_frequency'],
        task_arrive_probabilities=hyperparameters['task_arrive_probabilities'],
        task_size_mins=hyperparameters['task_size_mins'],
        task_size_maxs=hyperparameters['task_size_maxs'],
        task_size_distributions=hyperparameters['task_size_distributions'],
        timeout_delay_mins=hyperparameters['timeout_delay_mins'],
        timeout_delay_maxs=hyperparameters['timeout_delay_maxs'],
        timeout_delay_distributions=hyperparameters['timeout_delay_distributions'],
        priotiry_mins=hyperparameters['priotiry_mins'],
        priotiry_maxs=hyperparameters['priotiry_maxs'],
        priotiry_distributions=hyperparameters['priotiry_distributions'],
        computational_density_mins=hyperparameters['computational_density_mins'],
        computational_density_maxs=hyperparameters['computational_density_maxs'],
        computational_density_distributions=hyperparameters['computational_density_distributions'],
        drop_penalty_mins=hyperparameters['drop_penalty_mins'],
        drop_penalty_maxs=hyperparameters['drop_penalty_maxs'],
        drop_penalty_distributions=hyperparameters['drop_penalty_distributions'],
        trace_recorder=trace_recorder
    )
    
    
    scheduler_file= args.log_folder+'/scheduler.pth'
    scheduler_choices ={
        'constant': constant,
        'Linear': Linear(start=hyperparameters['learning_rate'],
                        end=hyperparameters['learning_rate_end'],
                            number_of_epochs=hyperparameters['lr_scheduler_epochs'])
        }
    
    scheduler =scheduler_choices[hyperparameters['scheduler_choice']]
    
    
    with open(scheduler_file, 'wb') as f:
        pickle.dump(scheduler, f)
    
    decision_makers = []
    
    decision_makers_choice = {
        "drl": Agent,
        "all_horizontal": AllHorizontal,
        "all_local": AllLocal,
        "all_vertical": AllVertical,
        "random": Random,
        "round_robin": RoundRobin,
        "rule_based": RuleBased,
        "single": SingleAgent,
        "HOODIE": Agent,
        "RO": Random,
        "FLC": AllLocal,
        "VO": AllVertical,
        "HO": AllHorizontal,
        "BCO": BalancedCyclicOffloader,
        "MLEO": MinimumLatencyEstimationOffloader,
    }
    chosen_descision_maker = decision_makers_choice[hyperparameters['decision_makers']]
    print("Baseline policy aliases:", official_policy_map())

    decision_makers = []
    
    
    for i in range(number_of_servers):
        state_dimensions,foreign_queues,number_of_actions = env.get_server_dimensions(i)      
        lstm_shape = foreign_queues 

        decision_maker_params ={'number_of_actions': number_of_actions} 
        
        if hyperparameters['decision_makers'] == 'drl':
            decision_maker_params = {
                'id': i,
                'state_dimensions': state_dimensions,
                'lstm_shape': lstm_shape,
                'number_of_actions': number_of_actions,
                'hidden_layers': hyperparameters['hidden_layers'],
                'lstm_layers': hyperparameters['lstm_layers'],
                'lstm_time_step': hyperparameters['lstm_time_step'],
                'dropout_rate': hyperparameters['dropout_rate'],
                'dueling': hyperparameters['dueling'],
                'epsilon': hyperparameters['epsilon'],
                'epsilon_decrement': hyperparameters['epsilon_decrement'],
                'epsilon_end': hyperparameters['epsilon_end'],
                'gamma': hyperparameters['gamma'],
                'learning_rate': hyperparameters['learning_rate'],
                'scheduler_file':scheduler_file,
                'loss_function': getattr(torch.nn, hyperparameters['loss_function']),
                'optimizer': getattr(torch.optim, hyperparameters['optimizer']),
                'checkpoint_folder': args.log_folder+ '/agent_'+str(i)+'.pth',
                'save_model_frequency': hyperparameters['save_model_frequency'],
                'update_weight_percentage': hyperparameters['update_weight_percentage'],
                'memory_size': hyperparameters['memory_size'],
                'batch_size': hyperparameters['batch_size'],
                'replace_target_iter': hyperparameters['replace_target_iter'],
                'device': device
            }
        
        if hyperparameters['decision_makers'] == 'rule_based':
            foreign_cpus = env.get_foreign_cpus(i)
            decision_maker_params = {
                'number_of_actions': number_of_actions,
                'local_cpu': hyperparameters['private_cpu_capacities'][i],
                'foreign_cpus':foreign_cpus
            }
        if hyperparameters['decision_makers'] == 'MLEO':
            decision_maker_params = {
                'number_of_actions': number_of_actions,
                'env': env,
                'source_id': i,
                'matchmaker': env.matchmakers[i],
            }
        
    
        decision_maker = chosen_descision_maker(**decision_maker_params)
        decision_makers.append(decision_maker)
        
        
        
    for key in hyperparameters:
        if key != 'connection_matrix':
            print(key ," : ",hyperparameters[key])
    for epoch in range(args.epochs):
        if epoch % episode_log_interval == 0:
            print(f"[main] starting episode {epoch}/{args.epochs - 1}", flush=True)
        accumulated_rewards = []
        env.episode_id = epoch
        observations,done, info = env.reset()
        local_observations,public_queues =observations
        while not done:
            step_time = env.current_time
            actions = np.zeros(number_of_servers, dtype=int)
            pending_transition_inputs = []
            for i in range(number_of_servers):
                paper_state = env.get_paper_state(i)
                trace_recorder.note_paper_state(
                    episode_id=paper_state["episode_id"],
                    time=paper_state["time"],
                    agent_id=i,
                    task_id=paper_state["task_id"],
                    eta_n=paper_state["eta_n"],
                    w_priv_n=paper_state["w_priv_n"],
                    w_off_n=paper_state["w_off_n"],
                    l_pub_n_prev=paper_state["l_pub_n_prev"],
                    active_load_vector=paper_state["active_load_vector"],
                    load_history=paper_state["L_t"],
                    predicted_next_load=paper_state["predicted_next_load"],
                    predicted_next_load_method=paper_state["predicted_next_load_method"],
                    paper_lstm_forecast=paper_state["paper_lstm_forecast"],
                    unavailable_fields=paper_state["unavailable_fields"],
                    approximation_warnings=paper_state["approximation_warnings"],
                    state_vector=paper_state["state_vector"],
                )
                current_task = env.tasks[i]
                if current_task is not None and not current_task.is_empty():
                    pending_transition_inputs.append(
                        {
                            "task_id": int(current_task.task_id),
                            "episode_id": epoch,
                            "source_agent": i,
                            "arrival_time": int(current_task.arrival_time),
                            "decision_time": step_time,
                            "state_at_decision": np.asarray(local_observations[i], dtype=np.float32).copy(),
                            "lstm_state_at_decision": np.asarray(public_queues[i], dtype=np.float32).copy(),
                            "created_by_policy": type(decision_makers[i]).__name__,
                        }
                    )
                actions[i] = decision_makers[i].choose_action(local_observations[i],public_queues[i])
            observations,rewards,done,info = env.step(actions)
            local_observations_,public_queues_ =observations
            for i in range(number_of_servers):
                action_decision = env.last_action_decisions[i]
                target_node = action_decision.legacy_target_node_id if action_decision is not None else env.matchmakers[i].match_action(i, actions[i])
                trace_recorder.note_action(
                    episode_id=epoch,
                    time=step_time,
                    agent_id=i,
                    observation_shape=np.shape(local_observations[i]),
                    selected_action=int(actions[i]),
                    target_node=int(target_node),
                    reward_received=float(rewards[i]),
                    first_stage_decision=None if action_decision is None else action_decision.first_stage_decision,
                    destination_node_id=None if action_decision is None else action_decision.destination_node_id,
                    destination_type=None if action_decision is None else action_decision.destination_type,
                    is_valid=None if action_decision is None else action_decision.is_valid,
                    invalid_reason=None if action_decision is None else action_decision.invalid_reason,
                    adjacency_allowed=None if action_decision is None else action_decision.adjacency_allowed,
                    cloud_target=None if action_decision is None else action_decision.cloud_target,
                    d_n_1=None if action_decision is None else action_decision.d_n_1,
                    d_nk_2=None if action_decision is None else action_decision.d_nk_2,
                )
            for entry in pending_transition_inputs:
                source_agent = entry["source_agent"]
                action_decision = env.last_action_decisions[source_agent]
                target_node = action_decision.legacy_target_node_id if action_decision is not None else env.matchmakers[source_agent].match_action(source_agent, actions[source_agent])
                trace_recorder.note_pending_transition(
                    task_id=entry["task_id"],
                    episode_id=entry["episode_id"],
                    source_agent=source_agent,
                    arrival_time=entry["arrival_time"],
                    decision_time=entry["decision_time"],
                    state_at_decision=entry["state_at_decision"],
                    lstm_state_at_decision=entry["lstm_state_at_decision"],
                    action_at_decision=int(actions[source_agent]),
                    selected_target_node=int(target_node),
                    raw_action_id=None if action_decision is None else int(action_decision.raw_action_id),
                    first_stage_decision=None if action_decision is None else action_decision.first_stage_decision,
                    destination_type=None if action_decision is None else action_decision.destination_type,
                    destination_node_id=None if action_decision is None else action_decision.destination_node_id,
                    immediate_next_state_after_action=local_observations_[source_agent],
                    immediate_next_lstm_state_after_action=public_queues_[source_agent],
                    created_by_policy=entry["created_by_policy"],
                    replay_pairing_status="pending",
                )
            delayed_reward_events = trace_recorder.resolve_delayed_reward_candidates(epoch)
            process_delayed_reward_events(decision_makers, trace_recorder, delayed_reward_events)
            if not args.validate:
                for i in range(number_of_servers):
                        pass
                        
            local_observations,public_queues  = local_observations_,public_queues_
            accumulated_rewards.append(sum(rewards))

        print(f'Epoch {epoch} Accumulated rewards: {sum(accumulated_rewards)/len(accumulated_rewards)}')
        trace_recorder.finalize_episode(epoch, total_reward=float(sum(accumulated_rewards)), mean_reward=float(sum(accumulated_rewards)/len(accumulated_rewards)) if accumulated_rewards else 0.0)
        if (epoch + 1) % episode_log_interval == 0 or epoch == args.epochs - 1:
            print(f"[main] finished episode {epoch}", flush=True)
        if not args.validate:
            for decision_maker in decision_makers:
                decision_maker.learn() 
                decision_maker.reset_lstm_history()
    trace_recorder.export(args.trace_output_dir)

                                
                    
if __name__ == "__main__":
    main()
