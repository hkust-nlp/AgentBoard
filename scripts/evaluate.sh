CUDA_VISIBLE_DEVICES=0,1,2,3 python agentboard/eval_main.py --cfg eval_configs/main_results_all_tasks.yaml \
                    --tasks alfworld \
                    --model  lemur-70b \
                    --log_path results/lemur-70b \
                    --wandb \
                    --project_name evaluate-lemur-70b \
                    --baseline_dir data/baseline_results \