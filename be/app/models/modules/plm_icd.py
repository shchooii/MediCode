import torch
import torch.utils.checkpoint
from torch import nn
from typing import Optional

from transformers import RobertaModel, AutoConfig
from .attention import LabelAttention



class PLMICD(nn.Module):
    def __init__(self, num_classes: int, model_path: str,
                 cls_num_list = None, 
                 head_idx = None, tail_idx = None,
                 co_occurrence_matrix = None,
                 class_freq = None, neg_class_freq = None,
                 **kwargs):
        super().__init__()
        self.config = AutoConfig.from_pretrained(
            model_path, num_labels=num_classes, finetuning_task=None
        )
        
        self.roberta = RobertaModel(
            self.config, add_pooling_layer=False
        ).from_pretrained(model_path, config=self.config)
        
        self.attention = LabelAttention(
            input_size=self.config.hidden_size,
            projection_size=self.config.hidden_size,
            num_classes=num_classes,
        )
        
        
        self.loss = torch.nn.functional.binary_cross_entropy_with_logits
        
        # self.loss = FocalLoss()
        
        # self.loss = Hill()

        # self.loss = AsymmetricLoss()
        
        # self.loss = MultiGrainedFocalLoss()
        # self.loss.create_weight(cls_num_list)
        
        # self.loss = PriorFocalModifierLoss()
        # self.loss.create_co_occurrence_matrix(co_occurrence_matrix)
        # self.loss.create_weight(cls_num_list)
        
        # self.loss = ResampleLoss(
        #     use_sigmoid    = True,
        #     class_freq     = class_freq,
        #     neg_class_freq = neg_class_freq,
        #     reweight_func  ='rebalance',
        # )
        
        # self.loss = ResampleLoss( # CB Loss
        #     use_sigmoid=True,                 
        #     reweight_func='CB',                             
        #     class_freq=class_freq,
        #     neg_class_freq=neg_class_freq
        # )
        
        # self.loss = DRLoss()
        
        # self.loss = APLLoss()
        
        # self.loss = Ralloss()
        
        # self.loss = ReflectiveLabelCorrectorLoss(num_classes=num_classes, distribution=cls_num_list)
    
    def get_loss(self, logits, targets):
        return self.loss(logits, targets)

    def training_step(self, batch) -> dict[str, torch.Tensor]:
        data, targets, attention_mask = batch.data, batch.targets, batch.attention_mask
        logits = self(data, attention_mask)
        loss = self.get_loss(logits, targets)
        logits = torch.sigmoid(logits)
        return {"logits": logits, "loss": loss, "targets": targets}


    def validation_step(self, batch) -> dict[str, torch.Tensor]:
        data, targets, attention_mask = batch.data, batch.targets, batch.attention_mask
        logits = self(data, attention_mask)
        loss = self.get_loss(logits, targets)
        logits = torch.sigmoid(logits)
        return {"logits": logits, "loss": loss, "targets": targets}

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
    ):
        r"""
        input_ids (torch.LongTensor of shape (batch_size, num_chunks, chunk_size))
        labels (:obj:`torch.LongTensor` of shape :obj:`(batch_size, num_labels)`, `optional`):
        """

        batch_size, num_chunks, chunk_size = input_ids.size()
        outputs = self.roberta(
            input_ids.view(-1, chunk_size),
            attention_mask=attention_mask.view(-1, chunk_size)
            if attention_mask is not None
            else None,
            return_dict=False,
        )

        hidden_output = outputs[0].view(batch_size, num_chunks * chunk_size, -1)
        logits = self.attention(hidden_output)
        return logits