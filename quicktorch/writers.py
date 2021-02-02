from collections import OrderedDict
try:
    import labscribe
except Exception:
    pass


class MetricWriter():
    """Base class for metrics writer
    """
    def __init__(self):
        pass


class LabScribeWriter(MetricWriter):
    """Writer for using gsheets with labscribe.
    """
    def __init__(self, sheet_name, exp_name=None, exp_worksheet_name=None, metrics_worksheet_name=None, nsplits=1):
        self.sheet_name = sheet_name
        self.exp_name = exp_name
        self.exp_worksheet_name = exp_worksheet_name
        self.metrics_worksheet_name = metrics_worksheet_name
        self.phase_cols = None
        self.nsplits = nsplits
        self.split = 1
        self.split_rows = [None] * nsplits
        self.iter = 1

    def begin_experiment(self, args):
        if self.exp_name is None:
            self.exp_name = '-'.join([f'{key}={val}' for key, val in args.items()])
        name = self.exp_name

        cell = labscribe.googlesheets.begin_experiment(
            self.sheet_name,
            name,
            args,
            worksheet_name=self.exp_worksheet_name
        )

        self.exp_row = cell.row
        self.n_args = len(args)

    def upload_split(self, results):
        # Past experiment arguments with space, find split's col with space for best split
        # split_col = self.n_args + 5 + len(results) * self.split
        split_col = 3 + (len(results) + 1) * self.split

        labscribe.googlesheets.upload_results(
            self.sheet_name,
            self.exp_name,
            OrderedDict(**results, exp_row=f'A{self.split_rows[self.split-1]}:Z{(self.split_rows[self.split-1] + self.iter + 1)}'),
            worksheet_name=self.exp_worksheet_name,
            row=self.exp_row,
            col=split_col
        )
        self.split += 1
        self.iter = 1

    def upload_best_split(self, results, split):
        # Past experiment arguments with space, find split's col with space for best split
        # split_col = self.n_args + 5
        split_col = 3

        labscribe.googlesheets.upload_results(
            self.sheet_name,
            self.exp_name,
            OrderedDict(**results, exp_row=f'A{self.split_rows[split-1]}:Z{(self.split_rows[split-1] + self.iter + 1)}'),
            worksheet_name=self.exp_worksheet_name,
            row=self.exp_row,
            col=split_col
        )
        self.split += 1
        self.iter = 1

    def start(self, metrics, phases=None):
        # labscribe.googlesheets.clear_worksheet(
        #     self.sheet_name,
        #     self.metrics_worksheet_name
        # )
        metric_keys = list(metrics.keys())
        if phases is None:
            phases = [None]
        self.phases = phases
        self.split_rows[self.split-1], self.phase_cols = labscribe.googlesheets.init_metrics(
            self.sheet_name,
            self.exp_name,
            metric_keys,
            worksheet_name=self.metrics_worksheet_name,
            phases=phases
        )

    def add(self, metrics, phase=None):
        labscribe.googlesheets.upload_metrics(
            self.sheet_name,
            metrics,
            self.metrics_worksheet_name,
            iter=self.iter,
            col=self.phase_cols[phase]
        )
        if phase == self.phases[-1]:
            self.iter += 1
