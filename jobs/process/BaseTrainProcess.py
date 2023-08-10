from datetime import datetime
import os
from collections import OrderedDict
from typing import TYPE_CHECKING, Union

import yaml

from jobs.process.BaseProcess import BaseProcess

if TYPE_CHECKING:
    from jobs import TrainJob, BaseJob, ExtensionJob
    from torch.utils.tensorboard import SummaryWriter
    from tqdm import tqdm


class BaseTrainProcess(BaseProcess):
    process_id: int
    config: OrderedDict
    writer: 'SummaryWriter'
    job: Union['TrainJob', 'BaseJob', 'ExtensionJob']
    progress_bar: 'tqdm' = None

    def __init__(
            self,
            process_id: int,
            job,
            config: OrderedDict
    ):
        super().__init__(process_id, job, config)
        self.progress_bar = None
        self.writer = None
        self.training_folder = self.get_conf('training_folder', self.job.training_folder)
        self.save_root = os.path.join(self.training_folder, self.job.name)
        self.step = 0
        self.first_step = 0
        self.log_dir = self.get_conf('log_dir', self.job.log_dir)
        self.setup_tensorboard()
        self.save_training_config()

    def run(self):
        super().run()
        # implement in child class
        # be sure to call super().run() first
        pass

    # def print(self, message, **kwargs):
    def print(self, *args):
        if self.progress_bar is not None:
            self.progress_bar.write(' '.join(map(str, args)))
            self.progress_bar.update()
        else:
            print(*args)

    def setup_tensorboard(self):
        if self.log_dir:
            from torch.utils.tensorboard import SummaryWriter
            now = datetime.now()
            time_str = now.strftime('%Y%m%d-%H%M%S')
            summary_name = f"{self.name}_{time_str}"
            summary_dir = os.path.join(self.log_dir, summary_name)
            self.writer = SummaryWriter(summary_dir)

    def save_training_config(self):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        os.makedirs(self.training_folder, exist_ok=True)
        save_dif = os.path.join(self.training_folder, f'process_config_{timestamp}.yaml')
        with open(save_dif, 'w') as f:
            yaml.dump(self.raw_process_config, f)
