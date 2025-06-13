import pandas as pd
import numpy as np
import os

def convert_balltask_csv_to_bids(infile, filename_prefix="sub-"):
    # Load slider responses
    slider_outputs = pd.read_csv(infile.replace('roi_outputs', 'slider_questions'))
    slider_outputs = slider_outputs[~slider_outputs["run"].isna()]
    slider_outputs.reset_index(drop=True, inplace=True)

    # Load main signal CSV
    df = pd.read_csv(infile)

    # Rename base columns
    rename_dict = {
        'time': 'onset',
        'stage': 'trial_type',
        'volume': 'feedback_source_volume',
        'pda_val': 'pda_value',         # legacy compatibility
        'pda_label': 'pda_label'
    }
    for roi in ['cen', 'dmn', 'smcl', 'smcr']:
        if roi in df.columns:
            rename_dict[roi] = f'{roi}_signal'
    df.rename(columns=rename_dict, inplace=True)

    # Ensure numeric columns are really numeric
    for col in ['pda_value', *[f'{roi}_signal' for roi in ['cen', 'dmn', 'smcl', 'smcr']]]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Add duration column (BIDS required)
    df['duration'] = 0

    # Parse pda_label to extract which ROI pair was used
    if 'pda_label' in df.columns:
        df['roi1'] = df['pda_label'].apply(lambda x: x.split('_')[0] if isinstance(x, str) else 'roi1')
        df['roi2'] = df['pda_label'].apply(lambda x: x.split('_')[1] if isinstance(x, str) else 'roi2')
    else:
        df['roi1'], df['roi2'] = 'roi1', 'roi2'

    # Compute hits per ROI (if cumulative columns available)
    for roi in ['cen', 'dmn', 'smcl', 'smcr']:
        cum_col = f'{roi}_cumulative_hits'
        hit_col = f'{roi}_hit'
        if cum_col in df.columns:
            df[hit_col] = np.where(df[cum_col].diff(periods=-1) == -1, 1, 0)
        else:
            df[hit_col] = 0

    # Subject metadata
    participant_numeric = str(slider_outputs['id'][0])
    run_num = int(slider_outputs['run'][0])
    feedback_flag = str(slider_outputs['feedback_on'][0])

    df['participant'] = f"{filename_prefix}{participant_numeric}"
    df['run'] = run_num
    df['feedback_on'] = feedback_flag

    def get_slider_response(q_text):
        try:
            return slider_outputs.loc[slider_outputs.question_text == q_text, 'response'].values[0]
        except:
            return 'n/a'

    df['slider_describing'] = get_slider_response('How often were you using the Mindful Describing practice?')
    df['slider_ballcheck'] = get_slider_response('How often did you check the position of the ball?')
    df['slider_difficulty'] = get_slider_response('How difficult was it to apply Mindful Describing?')
    df['slider_calm'] = get_slider_response('How calm do you feel right now?')

    # Fill object-type NaNs
    df[df.select_dtypes(include='object').columns] = df.select_dtypes(include='object').fillna('n/a')

    # Final output columns
    roi_signal_columns = [f'{roi}_signal' for roi in ['cen', 'dmn', 'smcl', 'smcr'] if f'{roi}_signal' in df.columns]
    hit_columns = [f'{roi}_hit' for roi in ['cen', 'dmn', 'smcl', 'smcr'] if f'{roi}_hit' in df.columns]

    core_columns = [
        'onset', 'duration', 'trial_type', 'feedback_source_volume',
        *roi_signal_columns, 'pda_value', 'pda_label',
        'ball_y_position', *hit_columns,
        'scale_factor', 'participant', 'run', 'feedback_on',
        'slider_describing', 'slider_ballcheck', 'slider_difficulty', 'slider_calm'
    ]

    out_df = df[core_columns]

    # Define BIDS-compliant run type
    if feedback_flag == 'Feedback':
        run_type = 'feedback'
    else:
        run_type = 'transferpre' if run_num == 1 else 'transferpost'
        run_num = 1 if run_num == 2 else 2

    output_dir = os.path.dirname(infile)
    subject_folder = os.path.basename(output_dir)
    outfile = os.path.join(
        output_dir,
        f"{subject_folder}_ses-nf_task-{run_type}_run-{run_num:02d}.tsv"
    )

    print(f"✅ Writing BIDS TSV: {outfile}")
    out_df.to_csv(outfile, sep='\t', index=False)

    return out_df

