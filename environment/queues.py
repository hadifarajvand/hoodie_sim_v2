from .task import Task
from utils import merge_dicts
import queue
import math
class TaskQueue():
    def __init__(self, queue_type:str="generic", node_id:int|None=None)->None:
        self.queue_type = queue_type
        self.node_id = node_id
        self.reset()
        
    def reset(self)->None:
        self.current_time=0
        self.queue_length = 0
        self.queue = queue.Queue()
        self.current_task = Task()
        self.arrivals_this_step = 0
        self.departures_this_step = 0
        self.drops_this_step = 0
    
    def add_task(self,
                 task:Task,
                 current_time:int|None=None)->None:
        if current_time is not None:
            task.queue_enter_time = current_time
        if self.is_empty():
            self.current_task = task.copy()
        else:
            self.queue.put(task.copy())
        self.queue_length += task.get_size()
        self.arrivals_this_step += 1
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None:
            recorder.note_queue_enter(task, episode_id=getattr(recorder, "_episode_id", None), time=current_time if current_time is not None else self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        
    def is_empty(self) -> bool:
        return self.queue.empty() and self.current_task.is_empty() 
    
    def current_task_is_timed_out(self)->bool:
        return self.current_time > self.current_task.get_timeout()

    def get_first_non_empty_element(self) ->int:
        self.current_time +=1
        rewards =  0
        if self.current_task.is_empty():
            if self.queue.empty():
                return rewards
            else:
                self.current_task = self.queue.get()
                recorder = getattr(Task, "trace_recorder", None)
                if recorder is not None and self.current_task.service_start_time is None:
                    self.current_task.service_start_time = self.current_time
                    recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        while self.current_task_is_timed_out():
            self.queue_length -= self.current_task.get_remaining_size()
            rewards += self.current_task.drop_task(drop_time=self.current_time, reason="timeout")
            if self.queue_type == "private":
                self.current_task.routing_metadata["paper_psi_priv"] = self.current_task.deadline_slot
                self.current_task.routing_metadata["paper_private_service_time"] = self.current_task.service_time
                self.current_task.routing_metadata["paper_private_final_status"] = "dropped"
                self.current_task.paper_psi_priv = self.current_task.deadline_slot
                self.current_task.paper_private_service_time = self.current_task.service_time
                self.current_task.paper_private_final_status = "dropped"
            if self.queue_type == "offloading":
                self.current_task.routing_metadata["paper_psi_off"] = self.current_task.deadline_slot
                self.current_task.routing_metadata["paper_off_final_status"] = "dropped"
                self.current_task.paper_psi_off = self.current_task.deadline_slot
                self.current_task.paper_off_final_status = "dropped"
            self.drops_this_step += 1
            recorder = getattr(Task, "trace_recorder", None)
            if recorder is not None:
                recorder.note_drop(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type, reason="timeout")
            if self.queue.empty():
                return rewards
            else:
                self.current_task = self.queue.get()
                recorder = getattr(Task, "trace_recorder", None)
                if recorder is not None and self.current_task.service_start_time is None:
                    self.current_task.service_start_time = self.current_time
                    recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        return rewards
    
    def get_waiting_time(self):
        raise NotImplementedError("Waiting time is not implemented for this queue (Probably public queue)")
    def get_queue_length(self):
        return self.queue_length

    def get_pending_tasks(self):
        tasks = []
        if not self.current_task.is_empty():
            tasks.append(self.current_task)
        tasks.extend(list(self.queue.queue))
        return tasks

    def get_trace_queue_length(self):
        total = 0.0
        if not self.current_task.is_empty():
            total += self.current_task.get_remaining_size()
        for item in list(self.queue.queue):
            total += item.get_remaining_size()
        return total

class ProcessingQueue(TaskQueue):
    def __init__(self,computational_capacity):
        super().__init__(queue_type="private")
        self.computational_capacity = computational_capacity
        self.waiting_time =0
        self.paper_latest_private_completion_slot = -1
        self.paper_latest_private_scheduled_completion_slot = -1
    def reset(self):
        super().reset()
        self.waiting_time =0      
        self.paper_latest_private_completion_slot = -1
        self.paper_latest_private_scheduled_completion_slot = -1

    def _paper_private_wait(self, current_time: int) -> int:
        return max(0, self.paper_latest_private_scheduled_completion_slot - current_time + 1)

    def _record_paper_private_enqueue(self, task, current_time: int) -> None:
        paper_w_priv = self._paper_private_wait(current_time)
        paper_private_service_time = math.ceil(task.get_size() / (self.computational_capacity / task.get_density()))
        scheduled_completion = current_time + paper_w_priv + paper_private_service_time - 1
        paper_psi_priv = min(scheduled_completion, task.deadline_slot)
        task.routing_metadata["paper_w_priv"] = paper_w_priv
        task.routing_metadata["paper_private_queue_enter_time"] = current_time
        task.routing_metadata["paper_private_deadline_slot"] = task.deadline_slot
        task.routing_metadata["paper_private_service_time"] = paper_private_service_time
        task.routing_metadata["paper_psi_priv"] = paper_psi_priv
        task.routing_metadata["paper_private_final_status"] = "scheduled"
        task.paper_w_priv = paper_w_priv
        task.paper_private_queue_enter_time = current_time
        task.paper_private_deadline_slot = task.deadline_slot
        task.paper_private_service_time = paper_private_service_time
        task.paper_psi_priv = paper_psi_priv
        task.paper_private_final_status = "scheduled"
        self.paper_latest_private_scheduled_completion_slot = max(self.paper_latest_private_scheduled_completion_slot, paper_psi_priv)

    def update_waiting_time(self,task):
        process_per_time_period = self.computational_capacity / task.get_density()
        time_to_process_task = math.ceil(task.get_size()/process_per_time_period)
        timeout_time = max(0,task.get_relative_timeout()-self.waiting_time)
        self.waiting_time += min(timeout_time,time_to_process_task)

    def _task_processing_time(self, task):
        process_per_time_period = self.computational_capacity / task.get_density()
        return math.ceil(task.get_remaining_size() / process_per_time_period)

    def get_waiting_time(self):
        if self.current_task.is_empty():
            return 0
        waiting = self._task_processing_time(self.current_task)
        for task in list(self.queue.queue):
            waiting += self._task_processing_time(task)
        return waiting
        
    def add_task(self,task, current_time=None):
        enqueue_time = self.current_time if current_time is None else current_time
        self._record_paper_private_enqueue(task, enqueue_time)
        super().add_task(task, current_time=enqueue_time)
        self.update_waiting_time(task)
        
        
    def step(self):
        if self.waiting_time>0:
            self.waiting_time -=1
        rewards = self.get_first_non_empty_element()
        if self.current_task.is_empty():
            return rewards
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None and self.current_task.service_start_time is None:
            self.current_task.service_start_time = self.current_time
            recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        rewards += self.current_task.process(self.computational_capacity,self.current_time)
        if self.current_task.is_empty():
            self.departures_this_step += 1
            recorder = getattr(Task, "trace_recorder", None)
            self.current_task.routing_metadata["paper_private_final_status"] = "completed"
            self.current_task.paper_private_final_status = "completed"
            self.current_task.routing_metadata["paper_private_service_time"] = self.current_task.routing_metadata.get("paper_private_service_time", self.current_task.service_time)
            self.current_task.paper_private_service_time = self.current_task.routing_metadata["paper_private_service_time"]
            if recorder is not None:
                recorder.note_service_end(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
            self.paper_latest_private_completion_slot = self.current_time
        return rewards
    
    

class OffloadingQueue(TaskQueue):
    def __init__(self,offloading_capacities, vertical_offloading_rate: float | None = None):   
        super().__init__(queue_type="offloading")
        self.offloading_capacities = offloading_capacities
        self.vertical_offloading_rate = float(vertical_offloading_rate) if vertical_offloading_rate is not None else 10.0
        self.paper_latest_offloading_scheduled_completion_slot = -1
        self.reset()
    def reset(self):
        super().reset()
        self.waiting_time =0
        self.paper_latest_offloading_scheduled_completion_slot = -1

    def _paper_off_wait(self, current_time: int) -> int:
        return max(0, self.paper_latest_offloading_scheduled_completion_slot - current_time + 1)

    def _resolve_off_rate(self, destination_node_id: int) -> tuple[str, float]:
        if destination_node_id == max(self.offloading_capacities.keys()):
            return "vertical", float(self.vertical_offloading_rate)
        return "horizontal", float(self.offloading_capacities[destination_node_id])

    def _record_paper_off_enqueue(self, task, current_time: int) -> None:
        paper_w_off = self._paper_off_wait(current_time)
        task.routing_metadata["paper_w_off"] = paper_w_off
        task.routing_metadata["paper_off_queue_enter_time"] = current_time
        task.routing_metadata["paper_off_deadline_slot"] = task.deadline_slot
        task.routing_metadata["paper_off_transmission_time"] = None
        task.routing_metadata["paper_psi_off"] = None
        task.routing_metadata["paper_off_rate_type"] = None
        task.routing_metadata["paper_off_rate_value"] = None
        task.routing_metadata["paper_off_destination_node_id"] = None
        task.routing_metadata["paper_off_final_status"] = "scheduled"
        task.routing_metadata["paper_off_scheduled_history_recorded"] = False
        task.paper_w_off = paper_w_off
        task.paper_off_queue_enter_time = current_time
        task.paper_off_deadline_slot = task.deadline_slot
        task.paper_off_transmission_time = None
        task.paper_psi_off = None
        task.paper_off_rate_type = None
        task.paper_off_rate_value = None
        task.paper_off_destination_node_id = None
        task.paper_off_final_status = "scheduled"
        task.paper_off_scheduled_history_recorded = False
    
    def update_waiting_time(self, task):
        target_server_id = task.get_target_server_id()
        if target_server_id is None:
            if task.routing_metadata.get("dm2_pending"):
                offloading_capacity = max(self.offloading_capacities.values())
            else:
                target_server_id = self._resolve_target_server_id(task)
                offloading_capacity = self.offloading_capacities[target_server_id]
        else:
            offloading_capacity = self.offloading_capacities[target_server_id]
        time_to_transmit_task =  math.ceil(task.get_size()/ offloading_capacity)
        timeout_time = max(0,task.get_relative_timeout()- self.waiting_time)
        self.waiting_time += min(timeout_time,time_to_transmit_task)

    def _task_transmission_time(self, task):
        target_server_id = task.get_target_server_id()
        if target_server_id is None:
            if task.routing_metadata.get("dm2_pending"):
                offloading_capacity = max(self.offloading_capacities.values())
            else:
                target_server_id = self._resolve_target_server_id(task)
                offloading_capacity = self.offloading_capacities[target_server_id]
        else:
            offloading_capacity = self.offloading_capacities[target_server_id]
        return math.ceil(task.get_remaining_size() / offloading_capacity)

    def resolve_dm2_destination(self, task):
        return self._resolve_target_server_id(task)

    def _resolve_target_server_id(self, task):
        target_server_id = task.get_target_server_id()
        if target_server_id is not None:
            return target_server_id
        destination = task.routing_metadata.get("paper_destination_node_id")
        if destination is None:
            dm2_destination_nodes = task.routing_metadata.get("dm2_destination_nodes")
            if dm2_destination_nodes is None:
                dm2_destination_nodes = sorted(self.offloading_capacities.keys())
            if not dm2_destination_nodes:
                raise ValueError("offloading task is missing a paper destination")
            destination = task.routing_metadata.get("dm2_destination_node_id")
            if destination is None:
                destination = dm2_destination_nodes[0]
        return int(destination)

    def get_waiting_time(self):
        if self.current_task.is_empty():
            return 0
        waiting = self._task_transmission_time(self.current_task)
        for task in list(self.queue.queue):
            waiting += self._task_transmission_time(task)
        return waiting
        
    
    def add_task(self,task, current_time=None):
        enqueue_time = self.current_time if current_time is None else current_time
        self._record_paper_off_enqueue(task, enqueue_time)
        super().add_task(task, current_time=enqueue_time)
        self.update_waiting_time(task)
        
    def step(self):
        if self.waiting_time>0:
            self.waiting_time -=1
        transmited_task = None
        reward = self.get_first_non_empty_element()
        if self.current_task.is_empty():
            return transmited_task,reward

        target_server_id = self.current_task.get_target_server_id()
        if target_server_id is None:
            target_server_id = self.resolve_dm2_destination(self.current_task)
            self.current_task.set_target_server_id(target_server_id)
        rate_type, offloading_capacity = self._resolve_off_rate(target_server_id)
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None and self.current_task.service_start_time is None:
            self.current_task.service_start_time = self.current_time
            recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        self.current_task.routing_metadata["dm2_timing"] = "offloading_queue_exit"
        self.current_task.routing_metadata["requires_separate_dm2_at_offloading_queue_exit"] = False
        self.current_task.routing_metadata["dm2_pending"] = False
        self.current_task.routing_metadata["paper_destination_node_id"] = int(target_server_id)
        self.current_task.routing_metadata["paper_off_destination_node_id"] = int(target_server_id)
        self.current_task.routing_metadata["paper_off_rate_type"] = rate_type
        self.current_task.routing_metadata["paper_off_rate_value"] = float(offloading_capacity)
        self.current_task.routing_metadata["paper_off_transmission_time"] = math.ceil(self.current_task.get_size() / offloading_capacity)
        paper_w_off = self.current_task.routing_metadata.get("paper_w_off", 0)
        paper_psi_off = min(
            int(self.current_task.routing_metadata.get("paper_off_queue_enter_time", self.current_time)) + int(paper_w_off) + int(self.current_task.routing_metadata["paper_off_transmission_time"]) - 1,
            self.current_task.deadline_slot,
        )
        self.current_task.routing_metadata["paper_psi_off"] = paper_psi_off
        self.current_task.routing_metadata["paper_off_final_status"] = "in_transmission"
        if not self.current_task.routing_metadata.get("paper_off_scheduled_history_recorded", False):
            self.paper_latest_offloading_scheduled_completion_slot = max(
                self.paper_latest_offloading_scheduled_completion_slot,
                int(paper_psi_off),
            )
            self.current_task.routing_metadata["paper_off_scheduled_history_recorded"] = True
            self.current_task.paper_off_scheduled_history_recorded = True
        paper_destination_nodes = self.current_task.routing_metadata.get("paper_destination_nodes")
        if not paper_destination_nodes:
            paper_destination_nodes = tuple(sorted(self.offloading_capacities.keys()))
            self.current_task.routing_metadata["paper_destination_nodes"] = list(paper_destination_nodes)
        if isinstance(paper_destination_nodes, list):
            paper_destination_nodes = tuple(paper_destination_nodes)
        if paper_destination_nodes:
            resolved_vector = [0 for _ in paper_destination_nodes]
            try:
                resolved_index = list(paper_destination_nodes).index(int(target_server_id))
            except ValueError:
                resolved_index = None
            if resolved_index is not None:
                resolved_vector[resolved_index] = 1
                self.current_task.routing_metadata["paper_d_nk_2"] = resolved_vector
        transmited_task = self.current_task.transmit(offloading_capacity)
        if transmited_task is not None:
            self.current_task.routing_metadata["paper_off_final_status"] = "transmitted"
            self.current_task.paper_off_final_status = "transmitted"
            transmited_task.routing_metadata["paper_w_off"] = paper_w_off
            transmited_task.routing_metadata["paper_psi_off"] = paper_psi_off
            transmited_task.routing_metadata["paper_off_queue_enter_time"] = self.current_task.routing_metadata.get("paper_off_queue_enter_time")
            transmited_task.routing_metadata["paper_off_transmission_time"] = self.current_task.routing_metadata.get("paper_off_transmission_time")
            transmited_task.routing_metadata["paper_off_deadline_slot"] = self.current_task.routing_metadata.get("paper_off_deadline_slot")
            transmited_task.routing_metadata["paper_off_rate_type"] = rate_type
            transmited_task.routing_metadata["paper_off_rate_value"] = float(offloading_capacity)
            transmited_task.routing_metadata["paper_off_destination_node_id"] = int(target_server_id)
            transmited_task.routing_metadata["paper_off_final_status"] = "transmitted"
            transmited_task.paper_w_off = paper_w_off
            transmited_task.paper_psi_off = paper_psi_off
            transmited_task.paper_off_queue_enter_time = self.current_task.routing_metadata.get("paper_off_queue_enter_time")
            transmited_task.paper_off_transmission_time = self.current_task.routing_metadata.get("paper_off_transmission_time")
            transmited_task.paper_off_deadline_slot = self.current_task.routing_metadata.get("paper_off_deadline_slot")
            transmited_task.paper_off_rate_type = rate_type
            transmited_task.paper_off_rate_value = float(offloading_capacity)
            transmited_task.paper_off_destination_node_id = int(target_server_id)
            transmited_task.paper_off_final_status = "transmitted"
            transmited_task.paper_off_scheduled_history_recorded = True
            transmited_task.routing_metadata["paper_off_scheduled_history_recorded"] = True
            recorder = getattr(Task, "trace_recorder", None)
            if recorder is not None:
                recorder.note_offloading_stage_end(
                    transmited_task,
                    episode_id=getattr(recorder, "_episode_id", None),
                    time=self.current_time,
                    node_id=self.node_id if self.node_id is not None else -1,
                    queue_type=self.queue_type,
                )
            self.departures_this_step += 1
        else:
            self.current_task.routing_metadata["paper_off_final_status"] = "in_transmission"
            self.current_task.paper_off_final_status = "in_transmission"
        return transmited_task,reward
    
class PublicQueue(TaskQueue):
    def __init__(self, node_id=None, source_id=None):
        super().__init__(queue_type="public", node_id=node_id)
        self.source_id = source_id
    def step(self,computational_capacity):
        reward = 0
        if self.current_task.is_empty():
            return reward
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None and self.current_task.service_start_time is None:
            self.current_task.service_start_time = self.current_time
            recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        reward, task_processed = self.current_task.public_process(computational_capacity,self.current_time)
        self.queue_length -= task_processed
        if self.current_task.is_empty():
            self.departures_this_step += 1
            if recorder is not None:
                recorder.note_service_end(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        return reward

    def estimate_waiting_time(self, computational_capacity: float) -> int:
        if self.is_empty():
            return 0
        waiting = 0
        for task in self.get_pending_tasks():
            waiting += math.ceil(task.get_remaining_size() * task.get_density() / computational_capacity)
        return waiting
                    

class PublicQueueManager():
    def __init__(self,
                 id,
                 computational_capacity,
                 supporting_servers):
        self.id = id
        self.computational_capacity = computational_capacity
        self.supporting_servers = supporting_servers
        self.public_queues ={}
        for server_id in self.supporting_servers:
            self.public_queues[server_id] = PublicQueue(node_id=self.id, source_id=server_id)
       
    
    def reset(self):
        for _,q in self.public_queues.items():
            q.reset()
    
    def get_public_queue_server_length(self,server_id):
        return self.public_queues[server_id].queue_length
    
    def get_priorities(self):
        active_queues = 0
        for _,q in self.public_queues.items():
            if not q.is_empty():
                active_queues += 1
        return active_queues
    def get_active_queues(self):
        active_queues =0
        for _,q in self.public_queues.items():
            if not q.is_empty():
                active_queues +=1
        return active_queues
        
    def add_tasks(self,recieved_tasks=[], current_time:int|None=None):
        for task in recieved_tasks:
            assert task.get_target_server_id() == self.id
            origin_server_id = task.get_origin_server_id()
            self.public_queues[origin_server_id].add_task(task, current_time=current_time)
    
    def step(self):
        drop_rewards ={}
        for server_id in self.supporting_servers:
            drop_rewards[server_id]= self.public_queues[server_id].get_first_non_empty_element()

        finished_rewards = {}
        active_queues= self.get_active_queues()
        total_priority = self.get_priorities()
        if active_queues!=0:
            distributed_computational_capacity = self.computational_capacity/active_queues
        else:
            distributed_computational_capacity = 0
       
        for server_id in self.supporting_servers:
            finished_rewards[server_id]= self.public_queues[server_id].step(distributed_computational_capacity)
         
        rewards = merge_dicts(drop_rewards,finished_rewards)
        return rewards
    
    
    def get_queue_lengths(self):
        queue_lengths = {}
        for server_id in self.supporting_servers:
            queue_lengths[server_id] = self.public_queues[server_id].get_queue_length()
        return queue_lengths

    def get_queue_snapshots(self):
        snapshots = {}
        for server_id in self.supporting_servers:
            snapshots[server_id] = self.public_queues[server_id].get_pending_tasks()
        return snapshots

    def estimate_waiting_time(self, source_id, candidate_becomes_active: bool = False):
        queue = self.public_queues[source_id]
        if queue.is_empty():
            return 0
        active_queues = self.get_active_queues()
        if candidate_becomes_active and queue.is_empty():
            active_queues += 1
        if active_queues == 0:
            return 0
        distributed_capacity = self.computational_capacity / active_queues
        return queue.estimate_waiting_time(distributed_capacity)
