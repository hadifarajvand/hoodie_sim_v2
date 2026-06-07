from __future__ import annotations

from numbers import Integral, Real

from .task import Task
from utils import Variabledistributor
import numpy as np


def _raise_preconstruction_validation_error(field_name, value, requirement):
    raise ValueError(
        f"TaskGenerator preconstruction validation failed for {field_name}: {value!r}. {requirement}"
    )


def _require_positive_number(field_name, value):
    if isinstance(value, bool) or not isinstance(value, Real) or float(value) <= 0:
        _raise_preconstruction_validation_error(field_name, value, "Expected a positive number.")


def _is_integer_like(value):
    return isinstance(value, Integral) or (isinstance(value, Real) and float(value).is_integer())


def _require_positive_integer(field_name, value):
    if isinstance(value, bool) or not _is_integer_like(value) or int(value) <= 0:
        _raise_preconstruction_validation_error(field_name, value, "Expected a positive integer.")


def _require_non_negative_integer(field_name, value):
    if isinstance(value, bool) or not _is_integer_like(value) or int(value) < 0:
        _raise_preconstruction_validation_error(field_name, value, "Expected a non-negative integer.")


class TaskGenerator():
    def __init__(self,
                id,
                episode_time,
                task_arrive_probability,
                size_min,
                size_max,
                size_distribution,
                timeout_delay_min,
                timeout_delay_max,
                timeout_delay_distribution,
                priotiry_min,
                priotiry_max,
                priotiry_distribution,
                computational_density_min,
                computational_density_max,
                computational_density_distribution,
                drop_penalty_min,   
                drop_penalty_max,
                drop_penalty_distribution,):
        self.id = id
        self.episode_time= episode_time
        self.task_arrive_probability = task_arrive_probability
        self.size_distributor =Variabledistributor(size_min,size_max,size_distribution)
        self.timeout_distributor =Variabledistributor(timeout_delay_min,timeout_delay_max,timeout_delay_distribution)
        self.priotiry_distributor =Variabledistributor(priotiry_min,priotiry_max,priotiry_distribution)
        self.computational_density_distributor =Variabledistributor(computational_density_min,computational_density_max,computational_density_distribution)
        self.drop_penalty_distributor =Variabledistributor(drop_penalty_min,drop_penalty_max,drop_penalty_distribution)
        self.current_time = 0
        self.size_max  = size_max
        self.timeout_delay_max = timeout_delay_max
        self.priotiry_max = priotiry_max
        self.computational_density_max = computational_density_max
        self.drop_penalty_max = drop_penalty_max
        
    def reset(self):
        self.current_time = -1
    def step(self):
        self.current_time +=1
        if self.current_time < self.episode_time:
            if np.random.rand() > self.task_arrive_probability:
                return None
            return self.generate()
        return None
   
    def generate(self):
        size = self.size_distributor.generate()
        timeout_delay = self.timeout_distributor.generate()
        priority = self.priotiry_distributor.generate()
        computational_density = self.computational_density_distributor.generate()
        drop_penalty = self.drop_penalty_distributor.generate()

        _require_positive_number("size", size)
        _require_positive_number("computational_density", computational_density)
        _require_positive_integer("timeout_delay", timeout_delay)
        _require_non_negative_integer("arrival_time", self.current_time)
        _require_non_negative_integer("drop_penalty", drop_penalty)
        _require_non_negative_integer("priority", priority)

        task = Task(
            size=size,
            arrival_time=self.current_time,
            timeout_delay=timeout_delay,
            priotiry=priority,
            computational_density=computational_density,
            drop_penalty=drop_penalty,
            origin_server_id=self.id,
            source_node_id=self.id,
            service_id=self.id,
            input_data_size=size,
            processing_density=computational_density,
            timeout=timeout_delay,
        )
        task.validate()
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None:
            recorder.note_task_arrival(task, episode_id=getattr(recorder, "_episode_id", None), source_node=self.id, arrival_time=self.current_time)
        return task
    def get_number_of_features(self):
       return self.generate().get_number_of_features()
   
    def get_maxs(self):
            return np.array([self.size_max])
