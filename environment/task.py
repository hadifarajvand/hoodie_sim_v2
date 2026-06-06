import numpy as np
class Task():
    next_task_id = 1
    trace_recorder = None
    def __init__(self,
                 size :float =None,
                 arrival_time :int=0,
                 timeout_delay:int=10,
                 priotiry:int=1,
                 computational_density:float=1,
                 drop_penalty :int=1,
                 origin_server_id:int=None,
                 target_server_id:int=None,
                 task_id:int=None,
                 ) -> None:
        if size :
            self.task_id = task_id if task_id is not None else Task.next_task_id
            Task.next_task_id = max(Task.next_task_id, self.task_id + 1)
            self.size = size
            self.remain = size
            self.arrival_time  = arrival_time
            self.timeout_delay = timeout_delay
            self.priotiry = priotiry
            self.computational_density = computational_density
            self.drop_penalty = drop_penalty
            self.timeout_instance = arrival_time + timeout_delay
            self.origin_server_id = origin_server_id
            self.target_server_id = target_server_id
            self.queue_enter_time = None
            self.service_start_time = None
            self.service_end_time = None
            self.completion_time = None
            self.drop_time = None
            self.selected_action = None
            self.processing_node = None
            self.latency = None
            self.waiting_time = None
            self.service_time = None
            self.final_status = "pending"
            self.drop_reason = None
            self.empty = False
        else:
            self.empty = True
            self.task_id = None
            
    def drop_task(self, drop_time:int=None, reason:str=None) -> int:
        self.empty = True
        if drop_time is not None:
            self.drop_time = drop_time
        self.final_status = "dropped"
        self.drop_reason = reason
        return self.drop_penalty
    
    
    def finish_task(self,
                    finish_time:int) ->int:
        self.empty = True
        self.service_end_time = finish_time
        self.completion_time = finish_time
        self.final_status = "completed"
        if self.service_start_time is not None:
            self.service_time = max(0, finish_time - self.service_start_time)
        if self.arrival_time is not None:
            self.latency = max(0, finish_time - self.arrival_time)
            if self.service_start_time is not None:
                self.waiting_time = max(0, self.service_start_time - self.arrival_time)
        return finish_time- self.arrival_time
    
    def is_empty(self) ->bool:
        return self.empty
    
        
    def process(self,capacity,time):
        self.remain -= capacity /self.computational_density
        if self.remain <=0:
            return self.finish_task(time)
        return 0

    def public_process(self,capacity,time):
        computational_capacity =  capacity  * self.priotiry
        task_processed = computational_capacity / self.computational_density
        self.remain -= task_processed
        if self.remain <=0:
            task_processed += self.remain
            return self.finish_task(time), task_processed
        return 0,task_processed

    def transmit(self,offloading_capacity):
        self.remain -= offloading_capacity
        if self.remain <=0:
            transmited_task =  Task(size = self.size,
                                arrival_time = self.arrival_time,
                                timeout_delay = self.timeout_delay,
                                priotiry=self.priotiry,
                                computational_density = self.computational_density,
                                drop_penalty = self.drop_penalty ,
                                origin_server_id= self.origin_server_id,
                                target_server_id = self.target_server_id,
                                task_id=self.task_id)
            transmited_task.queue_enter_time = self.queue_enter_time
            transmited_task.service_start_time = self.service_start_time
            transmited_task.processing_node = self.processing_node
            self.empty = True
            return transmited_task
        else:
            return None 

    def get_size(self):
        assert not self.empty
        return self.size
    def get_relative_timeout(self):
        assert not self.empty
        return self.timeout_delay
    def get_timeout(self):
        assert not self.empty
        return self.timeout_instance
    def get_remaining_size(self):
        assert not self.empty
        return self.remain
    
    def get_density(self):
        assert not self.empty
        return self.computational_density
    
    def get_priority(self):
        assert not self.empty
        return self.priotiry
    
    def get_target_server_id(self):
        assert not self.empty
        return self.target_server_id
    
    def get_origin_server_id(self):
        assert not self.empty
        return self.origin_server_id
    
    def set_origin_server_id(self,origin_server_id):
        assert not self.empty
        self.origin_server_id = origin_server_id
    
    def set_target_server_id(self,target_server_id:int)->None:
        assert not self.empty
        self.target_server_id = target_server_id
        
    def copy(self):
        copied = Task(size = self.size,
                    arrival_time = self.arrival_time,
                    timeout_delay = self.timeout_delay,
                    priotiry=self.priotiry,
                    computational_density = self.computational_density,
                    drop_penalty = self.drop_penalty ,
                    origin_server_id= self.origin_server_id,
                    target_server_id = self.target_server_id,
                    task_id=self.task_id)
        copied.queue_enter_time = self.queue_enter_time
        copied.service_start_time = self.service_start_time
        copied.service_end_time = self.service_end_time
        copied.completion_time = self.completion_time
        copied.drop_time = self.drop_time
        copied.selected_action = self.selected_action
        copied.processing_node = self.processing_node
        copied.latency = self.latency
        copied.waiting_time = self.waiting_time
        copied.service_time = self.service_time
        copied.final_status = self.final_status
        copied.drop_reason = self.drop_reason
        return copied
        
    def get_features(self):
        return np.array([self.size])
    def get_number_of_features(self):
        features =  self.get_features()
        return len(features)
