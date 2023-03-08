MODEL_NAME="MACE_Test"

train-model:
	python ./mace/scripts/run_train.py \
    	--name=${MODEL_NAME} \
    	--train_file="data/final/OCH.xyz" \
    	--valid_fraction=0.05 \
    	--config_type_weights='{"Default":1.0}' \
    	--E0s='{1:-13.663181292231226, 6:-1029.2809654211628, 7:-1484.1187695035828, 8:-2042.0330099956639}' \
    	--model="MACE" \
    	--hidden_irreps='128x0e + 128x1o' \
    	--r_max=5.0 \
    	--batch_size=10 \
    	--max_num_epochs=1500 \
    	--swa \
    	--start_swa=1200 \
    	--ema \
    	--ema_decay=0.99 \
    	--amsgrad \
    	--restart_latest \
    	--device=cuda \


test-train-model:
	python ./mace/scripts/run_train.py \
    	--name=${MODEL_NAME} \
    	--train_file="data/final/OCH.xyz" \
    	--valid_fraction=0.05 \
    	--config_type_weights='{"Default":1.0}' \
    	--E0s='{1:-13.663181292231226, 6:-1029.2809654211628, 7:-1484.1187695035828, 8:-2042.0330099956639}' \
    	--model="MACE" \
    	--hidden_irreps='128x0e + 128x1o' \
    	--r_max=5.0 \
    	--batch_size=10 \
    	--max_num_epochs=1500 \
		--default_dtype=float32 \
    	--swa \
    	--start_swa=1200 \
    	--ema \
    	--ema_decay=0.99 \
    	--amsgrad \
    	--restart_latest \
    	--device=cuda \