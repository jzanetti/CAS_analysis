####################################
# Basic setups
####################################
override PACKAGE = cat_analysis


####################################
# Conda/Mamba executable
####################################
override MAMBA_BASE= ~/Programs/miniconda3/envs/mamba/
override CONDA_BASE= ~/Programs/miniconda3/
override MAMBA = $(MAMBA_BASE)/bin/mamba
override CONDA = $(CONDA_BASE)/bin/conda
override CONDA_ENV_PATH = /tmp/opt/$(PACKAGE)
override FULL_TAG_LOCAL=cas_analysis


####################################
# makefile tasks
####################################
conda_remove_build:
	rm -rf $(CONDA_BASE)/../../pkgs/$(PACKAGE)*
	rm -rf $(CONDA_BASE)/../../conda-bld/linux-64/$(PACKAGE)*
	rm -rf $(CONDA_BASE)/../../conda-bld/$(PACKAGE)*
	$(CONDA) index $(CONDA_BASE)/conda-bld

conda_build: conda_remove_build
	GIT_DESCRIBE_TAG=$(GIT_TAG) GIT_DESCRIBE_NUMBER=$(GIT_NUMBER) $(MAMBA) build . --no-test -c conda-forge

conda_clean_up:
	$(MAMBA) env remove -p $(CONDA_ENV_PATH)


conda_install:
	$(MAMBA) install $(PACKAGE) -p $(CONDA_ENV_PATH) -c local -c conda-forge --force-reinstall

build_image:
	rm -rf env_$(PACKAGE).tar.gz
	$(CONDA) pack -p $(CONDA_ENV_PATH) -o env_$(PACKAGE).tar.gz
	docker image build --rm --tag $(FULL_TAG_LOCAL) -f Dockerfile .
	rm -rf env_$(PACKAGE).tar.gz

conda_create_env:
	mkdir -p /tmp/opt
	$(MAMBA) create -p $(CONDA_ENV_PATH)

install: conda_clean_up conda_build conda_create_env conda_install build_image

final_clean_up:
	rm -rf env_$(PACKAGE).tar.gz

# build and update the docker image to ECR
install_and_upload: install push_image final_clean_up

# build the local conda environment
build_conda_env_from_scratch: conda_clean_up conda_build conda_create_env conda_install final_clean_up