import pandas as pd
import argparse
from datetime import datetime, timedelta
from pathlib import Path

def process_data(name, group, period):
    def time(str):
        return datetime.fromisoformat(str)
    print(f"Processing group '{name}' with {len(group)} records.")
    period = timedelta(minutes=period)

    # Round up
    start = time(group['timestamp'].iloc[0])
    start += timedelta(microseconds=(1e6 - start.microsecond))
    start += timedelta(seconds=(60 - start.second))
    start += timedelta(minutes=((5 - start.minute) % 5))

    i = 0
    str = ""

    def dbg_print(s):
        pass
        # print(s)

    while True:
        j = i
        while j < len(group) and time(group['timestamp'].iloc[j]) - start < period:
            j += 1
        window = range(i,j)
        # time_window_start = 
        dbg_print(f"window:\t{window}")
        
        acc = 0.0

        if i > 0:
            val_pre = float(group['value'].iloc[i - 1])
            # time_pre = time(group['timestamp'].iloc[i - 1])
            dbg_print(f"before that, we had {group.iloc[i - 1]}")
            if len(window):
                acc += val_pre * (time(group['timestamp'].iloc[window.start]) - start).total_seconds()
                dbg_print(f"acc start at {acc}")
            else:
                acc += val_pre * period.total_seconds()
                dbg_print(f"acc start and done at {acc}")

        if len(window):
            dbg_print("yep")
            for idx in window[1:]:
                dbg_print(f"that includes {group.iloc[idx]}")
                weight = time(group['timestamp'].iloc[idx]) - time(group['timestamp'].iloc[idx - 1])
                val = group['value'].iloc[idx - 1]
                acc += float(weight.total_seconds()) * val
                dbg_print(f"acc {acc} contrib {weight}*{val}")
            
            idx = window.stop - 1
            weight = (start + period) - time(group['timestamp'].iloc[idx])
            val = group['value'].iloc[idx]
            acc += float(weight.total_seconds()) * val
            dbg_print(f"acc end {acc} contrib {weight}*{val}")

        dbg_print(acc)
        str += f"{start},{acc / period.total_seconds()}\n"
        
        if j >= len(group):
            break
        i = j
        start += period    

    return str

def main(input_files, output_dir, period):
    Path(output_dir).mkdir(exist_ok=True)

    for input_file in input_files:
        df = pd.read_csv(input_file)
        grouped = df.groupby([df.columns[0], df.columns[1], df.columns[2]])

        # Apply the process_data function to each group
        for name, group in grouped:
            s = process_data(name, group.iloc[:, 3:], period)
            fixed_name = '-'.join(name).replace(" ", "_")
            out_file = Path(output_dir) / f"{Path(input_file).stem}_{fixed_name}.csv"
            out_file.write_text(s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument("input_files", nargs='+', help="List of input CSV files to process")
    parser.add_argument("-o", "--output_dir", required=True, help="Directory to save the processed files")
    parser.add_argument("-p", "--period", required=True, help="Resampling/averaging period in minutes")
    
    args = parser.parse_args()
    main(args.input_files, args.output_dir, int(args.period))
